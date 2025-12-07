import pyvista as pv
import numpy as np

class Geometry:
    def __init__(self, geometry=None):
        self.geometry = geometry if geometry is not None else []

    def show(self, 
             iron_color="#A0A0A0",    
             magnet_color="#FF3333",  
             coil_color="#FF8C00",    
             air_color="#CCEEFF",     
             default_color="#3498DB"): 
        """
        Hiển thị 3D với bề mặt siêu mịn (Smooth Shading) và đầy đủ thông tin chi tiết.
        """
        if not self.geometry:
            print("Geometry is empty. Nothing to show.")
            return

        # --- 1. SETUP GIAO DIỆN ---
        pv.set_plot_theme("dark")
        plotter = pv.Plotter(window_size=[1200, 900])
        plotter.set_background("#0F0F0F") 
        plotter.add_axes()
        
        # --- 2. XỬ LÝ DỮ LIỆU & VẼ MESH ---
        print("Rendering high-quality geometry...")
        
        for segment in self.geometry:
            mesh_data = segment.mesh
            if mesh_data is None: continue

            try:
                # Wrap trimesh object
                pv_mesh = pv.wrap(mesh_data)
                
                # --- FIX LỖI KHÔNG TRƠN (SMOOTHING FIX) ---
                # Bước 1: Clean để gộp các điểm trùng nhau (quan trọng để shading hoạt động)
                pv_mesh = pv_mesh.clean()
                
                # Bước 2: Tính toán lại vector pháp tuyến tại các điểm (Point Normals)
                # split_vertices=True và feature_angle giúp giữ cạnh sắc ở góc vuông 
                # nhưng làm mềm ở bề mặt cong.
                pv_mesh = pv_mesh.compute_normals(point_normals=True, 
                                                  cell_normals=False, 
                                                  split_vertices=True, 
                                                  feature_angle=30.0, 
                                                  inplace=True)
            except Exception as e:
                print(f"Error processing mesh: {e}")
                continue

            # --- CẤU HÌNH VẬT LIỆU ---
            mat = str(segment.material).lower()
            
            # Default settings
            color = default_color
            opacity = 1.0; pbr = True; metallic = 0.5; roughness = 0.5

            if "iron" in mat or "steel" in mat: 
                color = iron_color
                metallic = 0.8; roughness = 0.3 # Kim loại bóng
            elif "magnet" in mat: 
                color = magnet_color
                metallic = 0.2; roughness = 0.6
            elif "copper" in mat or "coil" in mat: 
                color = coil_color
                metallic = 0.9; roughness = 0.2 # Đồng rất bóng
            elif "air" in mat: 
                color = air_color
                opacity = 0.05; pbr = False

            # --- TẠO INFO STRING ĐẦY ĐỦ ---
            # Helper để format vector gọn gàng
            def fmt_vec(v):
                if v is None: return "None"
                try: return f"[{v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f}]"
                except: return str(v)

            def fmt_val(v):
                if v is None: return "None"
                try: return f"{v:.4f}"
                except: return str(v)

            # Thu thập tất cả thuộc tính
            lines = []
            lines.append(f"Material      : {segment.material}")
            
            # Chỉ hiển thị nếu giá trị tồn tại (khác None hoặc khác 0 tùy ngữ cảnh)
            if hasattr(segment, 'magnet_source'):
                lines.append(f"Mag Source    : {fmt_val(segment.magnet_source)}")
            
            if hasattr(segment, 'magnetization_direction'):
                lines.append(f"Mag Direction : {fmt_vec(segment.magnetization_direction)}")
            
            if hasattr(segment, 'winding_vector'):
                lines.append(f"Winding Vec   : {fmt_vec(segment.winding_vector)}")
                
            if hasattr(segment, 'winding_normal'):
                lines.append(f"Winding Norm  : {fmt_vec(segment.winding_normal)}")
                
            if hasattr(segment, 'angular_length'):
                lines.append(f"Angular Len   : {fmt_val(segment.angular_length)}")
                
            if hasattr(segment, 'radial_length'):
                lines.append(f"Radial Len    : {fmt_val(segment.radial_length)}")
                
            if hasattr(segment, 'axial_length'):
                lines.append(f"Axial Len     : {fmt_val(segment.axial_length)}")

            full_info = "\n".join(lines)
            pv_mesh.field_data["info"] = [full_info]

            # --- VẼ ---
            plotter.add_mesh(pv_mesh, 
                             color=color, 
                             opacity=opacity,
                             show_edges=False,      
                             smooth_shading=True,   # Kết hợp với compute_normals ở trên
                             pbr=pbr,               
                             metallic=metallic,
                             roughness=roughness,
                             pickable=True)

        # --- 3. INTERACTION ---
        def on_pick(mesh):
            if mesh is None: return
            try:
                if "info" in mesh.field_data:
                    # Xóa text cũ nếu có (bằng cách overwrite name='hud_info')
                    plotter.add_text(
                        f"Geometry details \n{mesh.field_data['info'][0]}", 
                        position='upper_left', 
                        font_size=11, 
                        color='white', 
                        name='hud_info', 
                        font='courier', # Dùng font đơn cách để căn lề đẹp
                        shadow=True
                    )
            except Exception as e:
                print(e)

        plotter.enable_mesh_picking(on_pick, show=False, show_message=False)

        # --- 4. HOÀN TẤT ---
        plotter.add_text("HIGH QUALITY RENDER", position='upper_right', font_size=14, color='white')
        
        # Thêm đèn để tôn vinh độ bóng của bề mặt cong
        light = pv.Light(position=(500, 500, 1000), color='white', intensity=0.9)
        plotter.add_light(light)
        
        plotter.view_isometric()
        plotter.show()

        