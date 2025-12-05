import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

class Geometry:
    def __init__(self, geometry=None):
        self.geometry = geometry if geometry is not None else []

    def show(self, 
             iron_color=(0.7, 0.7, 0.7, 0.5),    # Light gray for dark mode
             magnet_color=(1.0, 0.3, 0.3, 0.8),  # Bright red
             coil_color=(0.9, 0.5, 0.2, 0.6),    # Bright copper
             air_color=(0.8, 0.9, 1.0, 0.1),     # Faint blue
             default_color=(0.2, 0.6, 1.0, 0.5), 
             linewidth=0.05):                    
        """
        Displays 3D Interactive Plot in Modern Dark Mode (English UI).
        """
        if not self.geometry:
            print("Geometry is empty.")
            return

        # --- MODERN STYLE: DARK BACKGROUND ---
        # Sử dụng context manager để chỉ áp dụng dark mode cho biểu đồ này
        with plt.style.context('dark_background'):
            
            fig = plt.figure(figsize=(14, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Tùy chỉnh giao diện trục cho hiện đại hơn
            ax.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.5)
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            
            artist_to_segment = {}
            all_min, all_max = [], []

            # --- Rendering Loop ---
            for segment in self.geometry:
                mesh = segment.mesh
                if mesh is None: continue

                polygons = mesh.vertices[mesh.faces]
                
                # Determine Color
                mat = str(segment.material).lower()
                if "iron" in mat or "steel" in mat: color = iron_color
                elif "magnet" in mat: color = magnet_color
                elif "copper" in mat or "coil" in mat or "winding" in mat: color = coil_color
                elif "air" in mat: color = air_color
                else: color = default_color

                # Edge color should be white/light in dark mode if linewidth > 0
                edge_color = 'white' if linewidth > 0 else 'none'
                edge_alpha = 0.3 if linewidth > 0 else 0

                # Create Collection
                mesh_collection = Poly3DCollection(
                    polygons, 
                    alpha=color[3], 
                    linewidths=linewidth, 
                    edgecolor=edge_color
                )
                mesh_collection.set_facecolor(color[:3])
                if linewidth > 0:
                    mesh_collection.set_edgecolor((1, 1, 1, edge_alpha))
                
                # Enable Interaction
                mesh_collection.set_picker(True) 
                
                ax.add_collection3d(mesh_collection)
                artist_to_segment[mesh_collection] = segment
                
                all_min.append(mesh.bounds[0])
                all_max.append(mesh.bounds[1])

            # --- HUD (Heads-Up Display) Info Box ---
            # Style: Dark semi-transparent box with white monospace text
            initial_text = "INTERACTIVE MODE\nClick on a segment\nto view details."
            
            info_text = fig.text(
                0.02, 0.90, initial_text, 
                fontsize=10, 
                color='white',
                verticalalignment='top', 
                family='monospace', # Font kiểu máy đánh chữ cho thẳng hàng
                bbox=dict(
                    boxstyle='round,pad=0.8', 
                    facecolor='#222222', # Dark gray background
                    edgecolor='gray',
                    alpha=0.85
                )
            )

            # --- Helper: Format Vector ---
            def fmt_vec(v):
                if isinstance(v, (np.ndarray, list, tuple)):
                    return f"[{v[0]:5.2f}, {v[1]:5.2f}, {v[2]:5.2f}]"
                return str(v)

            # --- Event Handler ---
            def on_pick(event):
                artist = event.artist
                if artist in artist_to_segment:
                    seg = artist_to_segment[artist]
                    
                    # Formatting Output (Aligned Columns)
                    lines = [f"== SEGMENT DETAILS =="]
                    lines.append(f"{'Material':<10}: {seg.material}")
                    
                    lines.append(f"\n[MAGNETIC PROPERTIES]")
                    lines.append(f"{'Source':<10}: {seg.magnet_source:.4f} T")
                    lines.append(f"{'Direction':<10}: {fmt_vec(seg.magnetization_direction)}")
                    
                    lines.append(f"\n[WINDING CONFIG]")
                    lines.append(f"{'Vector':<10}: {fmt_vec(seg.winding_vector)}")
                    lines.append(f"{'Normal':<10}: {fmt_vec(seg.winding_normal)}")
                    
                    lines.append(f"\n[GEOMETRY / DIMENSIONS]")
                    lines.append(f"{'Radial':<10}: {seg.radial_length:.4f} mm")
                    lines.append(f"{'Axial':<10}: {seg.axial_length:.4f} mm")
                    lines.append(f"{'Angular':<10}: {seg.angular_length:.4f} rad")

                    full_text = "\n".join(lines)
                    
                    # Update HUD
                    info_text.set_text(full_text)
                    
                    # Print to Console (Clean Log)
                    print(f"\n--- PICK EVENT DETECTED ---")
                    print(full_text)
                    
                    fig.canvas.draw_idle()

            fig.canvas.mpl_connect('pick_event', on_pick)

            # --- Auto Scaling ---
            if all_min and all_max:
                global_min = np.min(all_min, axis=0)
                global_max = np.max(all_max, axis=0)
                max_range = (global_max - global_min).max() / 2.0
                mid = (global_max + global_min) * 0.5
                ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
                ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
                ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

            # Modern Axis Labels
            ax.set_xlabel('X Axis (mm)', color='white')
            ax.set_ylabel('Y Axis (mm)', color='white')
            ax.set_zlabel('Z Axis (mm)', color='white')
            ax.set_title(f"3D MOTOR ASSEMBLY VIEW ({len(self.geometry)} Segments)", color='white', pad=20)
            
            # Remove gray background of the pane for cleaner look
            ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
            ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
            ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

            plt.show()