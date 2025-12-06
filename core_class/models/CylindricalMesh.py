import numpy as np
import pyvista as pv

class CylindricalMesh:
    def __init__(self, r_nodes=None, theta_nodes=None, z_nodes=None, periodic_boundary=True):
        """
        Khởi tạo lưới tọa độ trụ với 3 mảng đầu vào riêng biệt.

        Args:
            r_nodes (array-like): Mảng tọa độ các điểm chia theo bán kính (mm hoặc m).
            theta_nodes (array-like): Mảng tọa độ các điểm chia theo góc (radian).
            z_nodes (array-like): Mảng tọa độ các điểm chia theo trục dọc (mm hoặc m).
            periodic_boundary (bool): Cờ đánh dấu biên tuần hoàn (dùng cho trục theta trong động cơ).
        """
        # 1. Xử lý input mặc định
        if r_nodes is None:
            r_nodes = np.linspace(0, 1, 2)
        if theta_nodes is None:
            theta_nodes = np.linspace(0, np.pi, 2)
        if z_nodes is None:
            z_nodes = np.linspace(0, 1, 2)

        # 2. Lưu trữ các node biên (chuyển về numpy array để an toàn)
        self.r_nodes = np.array(r_nodes)
        self.theta_nodes = np.array(theta_nodes)
        self.z_nodes = np.array(z_nodes)
        
        self.periodic_boundary = periodic_boundary

        # 3. Tính số lượng node
        self.nr = len(self.r_nodes)
        self.nt = len(self.theta_nodes)
        self.nz = len(self.z_nodes)
        
        # 4. Tính số lượng phần tử (Cells)
        self.n_cells_r = max(1, self.nr - 1)
        self.n_cells_t = max(1, self.nt - 1)
        self.n_cells_z = max(1, self.nz - 1)
        
        self.total_cells = self.n_cells_r * self.n_cells_t * self.n_cells_z
        
        # 5. Tạo lưới 3D (Meshgrid)
        # indexing='ij' quan trọng để giữ thứ tự matrix (r, theta, z)
        self.R, self.Theta, self.Z = np.meshgrid(self.r_nodes, 
                                                 self.theta_nodes, 
                                                 self.z_nodes, 
                                                 indexing='ij')

        # 6. Chuyển đổi sang tọa độ Descartes (để vẽ đồ họa)
        self.X = self.R * np.cos(self.Theta)
        self.Y = self.R * np.sin(self.Theta)

    def get_cell_centers(self):
        """
        Trả về tọa độ tâm (r, theta, z) của các phần tử.
        Dùng để định vị node trong Mạng từ trở (Reluctance Network).
        """
        r_c = (self.r_nodes[:-1] + self.r_nodes[1:]) / 2
        t_c = (self.theta_nodes[:-1] + self.theta_nodes[1:]) / 2
        z_c = (self.z_nodes[:-1] + self.z_nodes[1:]) / 2
        
        R_c, T_c, Z_c = np.meshgrid(r_c, t_c, z_c, indexing='ij')
        return R_c, T_c, Z_c

    def get_cell_volumes(self):
        """
        Tính thể tích vi phân của từng phần tử: dV = r * dr * dtheta * dz
        """
        dr = np.diff(self.r_nodes)
        dtheta = np.diff(self.theta_nodes)
        dz = np.diff(self.z_nodes)
        
        r_c = (self.r_nodes[:-1] + self.r_nodes[1:]) / 2
        
        # Meshgrid cho các đại lượng delta
        DR, DTHETA, DZ = np.meshgrid(dr, dtheta, dz, indexing='ij')
        R_C, _, _ = np.meshgrid(r_c, dtheta, dz, indexing='ij')
        
        Volumes = R_C * DR * DTHETA * DZ
        return Volumes

    def to_pyvista_grid(self):
        """
        Chuyển đổi sang đối tượng pyvista.StructuredGrid.
        """
        grid = pv.StructuredGrid(self.X, self.Y, self.Z)
        
        # Tính toán thể tích để gán vào Cell Data (dùng cho visualization)
        try:
            # Flatten 'F' (Fortran order) thường khớp với cấu trúc topology của VTK/PyVista
            vols = self.get_cell_volumes().flatten(order='F')
            grid.cell_data["Volume"] = vols
        except Exception as e:
            print(f"Warning: Could not compute volumes for visualization: {e}")
            
        return grid

    def show(self, show_edges=True, notebook=False):
        """
        Hiển thị lưới 3D sử dụng PyVista (Dark Mode).
        """
        # 1. Chuẩn bị dữ liệu
        grid = self.to_pyvista_grid()
        
        # 2. Cài đặt Theme tối
        pv.set_plot_theme("dark")
        
        # 3. Khởi tạo Plotter
        plotter = pv.Plotter(notebook=notebook, window_size=[1200, 900])
        plotter.set_background("#1A1A1A") # Nền xám đen
        plotter.add_axes()

        # 4. Vẽ Mesh
        # Scalars='Volume' giúp tô màu để kiểm tra kích thước lưới
        plotter.add_mesh(grid, 
                         show_edges=show_edges,
                         scalars="Volume", 
                         cmap="viridis", 
                         opacity=0.9,
                         edge_color="#DDDDDD",
                         scalar_bar_args={"title": "Cell Volume"})
        
        # 5. Hiển thị Grid Box bao quanh
        plotter.show_grid(color='gray', font_size=10, grid=False, location='outer')

        # 6. Hiển thị thông số lưới (HUD)
        stats_text = (f"== MESH STATISTICS ==\n"
                      f"R nodes : {self.nr}\n"
                      f"T nodes : {self.nt}\n"
                      f"Z nodes : {self.nz}\n"
                      f"Total Cells: {self.total_cells}")
        
        plotter.add_text(stats_text, position='upper_left', font_size=10, font='courier', color='white')

        # 7. Show
        plotter.view_isometric()
        plotter.show()

        return plotter

# --- PHẦN CHẠY THỬ (TEST) ---
if __name__ == "__main__":
    print("Initializing Cylindrical Mesh...")
    
    # Tạo dữ liệu mẫu (ví dụ: một phần vành stator)
    r_arr = np.linspace(50, 80, 10)       # 10 điểm bán kính
    theta_arr = np.linspace(0, np.pi, 30) # 30 điểm góc (nửa vòng tròn)
    z_arr = np.linspace(0, 100, 5)        # 5 điểm dọc trục
    
    # Khởi tạo
    mesh = CylindricalMesh(r_nodes=r_arr, 
                           theta_nodes=theta_arr, 
                           z_nodes=z_arr)
    
    # In thông tin ma trận
    print(f"Mesh shape (R, T, Z matrices): {mesh.R.shape}")
    
    # Hiển thị 3D
    print("Displaying PyVista window...")
    mesh.show()

    