import numpy as np
import pyvista as pv

class CylindricalMesh:
    def __init__(self, coordinates=None, periodic_boundary=True):
        """
        Khởi tạo lưới tọa độ trụ.

        Args:
            coordinates (list/tuple/ndarray): Mảng chứa 3 thành phần [r_nodes, theta_nodes, z_nodes].
                                              Ví dụ: [np.array([1,2]), np.array([0, pi]), np.array([0, 10])]
            periodic_boundary (bool): Cờ đánh dấu biên tuần hoàn (dùng cho trục theta trong động cơ).
        """
        # Xử lý input mặc định nếu None
        if coordinates is None:
            # Tạo một lưới dummy mặc định để không bị lỗi code
            coordinates = [np.linspace(0, 1, 2), np.linspace(0, 1, 2), np.linspace(0, 1, 2)]

        # Unpack coordinates: Quy ước row 0 = r, row 1 = theta, row 2 = z
        self.r_nodes = np.array(coordinates[0])
        self.theta_nodes = np.array(coordinates[1])
        self.z_nodes = np.array(coordinates[2])
        
        self.periodic_boundary = periodic_boundary

        # Số lượng node
        self.nr = len(self.r_nodes)
        self.nt = len(self.theta_nodes)
        self.nz = len(self.z_nodes)
        
        # Số lượng phần tử (Cells) = số node - 1
        self.n_cells_r = max(1, self.nr - 1)
        self.n_cells_t = max(1, self.nt - 1)
        self.n_cells_z = max(1, self.nz - 1)

        self.total_cells = self.n_cells_r * self.n_cells_t * self.n_cells_z
        
        # --- TẠO LƯỚI 3D (MESHGRID) ---
        # indexing='ij' để giữ đúng thứ tự (r, theta, z)
        self.R, self.Theta, self.Z = np.meshgrid(self.r_nodes, 
                                                 self.theta_nodes, 
                                                 self.z_nodes, 
                                                 indexing='ij')

        # Chuyển đổi sang tọa độ Descartes (X, Y, Z) để phục vụ visualization
        self.X = self.R * np.cos(self.Theta)
        self.Y = self.R * np.sin(self.Theta)
        # self.Z đã có ở trên

    def get_cell_centers(self):
        """
        Trả về tọa độ tâm (r, theta, z) của các phần tử.
        Output là 3 ma trận 3D, shape (nr-1, nt-1, nz-1).
        """
        # Trung bình cộng các node liền kề
        r_c = (self.r_nodes[:-1] + self.r_nodes[1:]) / 2
        t_c = (self.theta_nodes[:-1] + self.theta_nodes[1:]) / 2
        z_c = (self.z_nodes[:-1] + self.z_nodes[1:]) / 2
        
        # Meshgrid cho tâm
        R_c, T_c, Z_c = np.meshgrid(r_c, t_c, z_c, indexing='ij')
        return R_c, T_c, Z_c

    def get_cell_volumes(self):
        """
        Tính thể tích vi phân dV = r * dr * dtheta * dz
        """
        # Tính sai phân (delta)
        dr = np.diff(self.r_nodes)
        dtheta = np.diff(self.theta_nodes)
        dz = np.diff(self.z_nodes)
        
        # Bán kính trung bình tại tâm phần tử
        r_c = (self.r_nodes[:-1] + self.r_nodes[1:]) / 2
        
        # Meshgrid cho các đại lượng delta
        DR, DTHETA, DZ = np.meshgrid(dr, dtheta, dz, indexing='ij')
        R_C, _, _ = np.meshgrid(r_c, dtheta, dz, indexing='ij') # Chỉ cần r thay đổi theo trục 0
        
        # V = r * dr * dtheta * dz
        Volumes = R_C * DR * DTHETA * DZ
        return Volumes

    def to_pyvista_grid(self):
        """
        Xuất sang đối tượng pyvista.StructuredGrid để vẽ 3D.
        """
        # Tạo grid cấu trúc từ tọa độ Descartes
        grid = pv.StructuredGrid(self.X, self.Y, self.Z)
        
        # Thử tính thể tích và gán vào cell data để kiểm tra (optional)
        try:
            # Flatten theo thứ tự Fortran ('F') để khớp với topology của PyVista StructuredGrid
            vols = self.get_cell_volumes().flatten(order='F')
            grid.cell_data["Volume"] = vols
        except Exception as e:
            print(f"Warning: Could not compute volumes for visualization: {e}")
            
        return grid

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # Tạo dữ liệu test: 
    # r: 10 điểm từ 20 đến 30
    # theta: 36 điểm từ 0 đến 2pi
    # z: 5 điểm từ 0 đến 50
    coords = [
        np.linspace(20, 30, 10),      # Row 0: r
        np.linspace(0, np.pi /3, 36),  # Row 1: theta
        np.linspace(0, 50, 5)         # Row 2: z
    ]
    
    # Khởi tạo class kiểu mới
    mesh = CylindricalMesh(coordinates=coords, periodic_boundary=True)
    
    # Hiển thị
    print(f"Shape R mesh: {mesh.R.shape}")
    pv_grid = mesh.to_pyvista_grid()
    pv_grid.plot(show_edges=True, show_grid=True)