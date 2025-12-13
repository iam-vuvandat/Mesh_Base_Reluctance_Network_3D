import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import QDockWidget, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

def show_reluctance_network(reluctance_network):
    mesh_obj = reluctance_network.mesh
    elements_matrix = reluctance_network.elements
    
    nr, nt, nz = elements_matrix.shape
    
    grid_pv = mesh_obj.to_pyvista_grid()
    flat_elements = elements_matrix.flatten(order='F')
    grid_pv.cell_data["OrigID"] = np.arange(grid_pv.n_cells)
    
    mat_ids = np.zeros(len(flat_elements), dtype=int)
    for idx, el in enumerate(flat_elements):
        if el is None: continue
        mat_name = str(el.material).lower()
        
        if "iron" in mat_name or "steel" in mat_name:
            mat_ids[idx] = 1
        elif "magnet" in mat_name:
            vec = getattr(el, 'magnetization_direction', None)
            z_val = vec[-1] if (vec is not None and len(vec) > 0) else 0
            
            if z_val > 0:
                mat_ids[idx] = 2 
            elif z_val < 0:
                mat_ids[idx] = 4 
            else:
                mat_ids[idx] = 2
        elif "coil" in mat_name or "winding" in mat_name:
            mat_ids[idx] = 3
        else:
            mat_ids[idx] = 0
            
    grid_pv.cell_data["MatID"] = mat_ids

    pl = BackgroundPlotter(title="Reluctance Network Viewer", window_size=(1600, 900))
    pl.set_background("#050505")
    pl.add_axes()

    dock = QDockWidget("Element Info", pl.app_window)
    dock_widget = QWidget()
    layout = QVBoxLayout()
    
    text_info = QTextEdit()
    text_info.setReadOnly(True)
    text_info.setStyleSheet("background-color: #1E1E1E; color: white; font-family: Consolas; font-size: 28px;")
    
    layout.addWidget(text_info)
    dock_widget.setLayout(layout)
    dock.setWidget(dock_widget)
    pl.app_window.addDockWidget(Qt.RightDockWidgetArea, dock)

    styles = {
        0: ("Default/Air", "#AAAAAA", 0.3),
        1: ("Iron",        "#F0F0F0", 0.8),
        2: ("Magnet N",    "#FF0000", 0.9),
        3: ("Coil",        "#FFAA00", 0.8),
        4: ("Magnet S",    "#0000FF", 0.9)
    }

    for mat_id, (label, color, opacity) in styles.items():
        sub_mesh = grid_pv.threshold([mat_id, mat_id], scalars="MatID", preference="cell")
        if sub_mesh.n_cells > 0:
            edge_color = "#222222" if mat_id == 0 else "#555555"
            pl.add_mesh(sub_mesh, color=color, opacity=opacity, 
                        show_edges=True, edge_color=edge_color, label=label,
                        pickable=True, line_width=2.0)

    pl.add_legend(bcolor='#1A1A1A', border=True, size=(0.12, 0.15), loc='lower right', face='rectangle')

    class ViewerState:
        def __init__(self):
            self.selected_idx = (0, 0, 0)
            self.highlight_actor = None 

        def update_selection(self, ir, it, iz):
            self.selected_idx = (ir, it, iz)
            flat_id = ir + it * nr + iz * (nr * nt)
            
            if self.highlight_actor:
                pl.remove_actor(self.highlight_actor)
            
            try:
                cell_geo = grid_pv.extract_cells([flat_id])
                self.highlight_actor = pl.add_mesh(cell_geo, style='wireframe', color='#00FFFF', 
                                                   line_width=5, render=False, name="highlight")
            except: pass

            element_obj = elements_matrix[ir, it, iz]
            
            info_str = f"=== SELECTED ELEMENT ===\n"
            info_str += f"Index (3D): [{ir}, {it}, {iz}]\n"
            info_str += f"Flat ID   : {flat_id}\n"
            info_str += "="*30 + "\n"
            
            if element_obj is None:
                info_str += "Status: Empty / None"
            else:
                attrs = vars(element_obj)
                for key, val in attrs.items():
                    if key.startswith("__"): continue
                    
                    info_str += f"\n[ {key} ]\n"
                    
                    if isinstance(val, np.ndarray):
                        with np.printoptions(formatter={'float': '{: 0.6f}'.format}, threshold=1000, linewidth=80):
                            arr_str = np.array2string(val, separator=', ')
                            info_str += f"{arr_str}\n"
                    elif isinstance(val, float):
                        info_str += f"{val:.9f}\n"
                    elif key in ['mesh', 'motor', 'geometry']:
                        info_str += f"<Reference to {type(val).__name__}>\n"
                    else:
                        info_str += f"{val}\n"

            text_info.setText(info_str)

        def move_cursor(self, dr, dt, dz):
            r, t, z = self.selected_idx
            r += dr
            t += dt
            z += dz

            while r >= nr: r -= nr; t += 1
            while r < 0:   r += nr; t -= 1
            while t >= nt: t -= nt; z += 1
            while t < 0:   t += nt; z -= 1
            z = z % nz 

            self.update_selection(r, t, z)

    state = ViewerState()

    def on_cell_picked(picked_mesh):
        if picked_mesh is None: return
        if isinstance(picked_mesh, pv.MultiBlock):
            if len(picked_mesh) == 0: return
            picked_mesh = picked_mesh[0]

        if not hasattr(picked_mesh, 'n_cells') or picked_mesh.n_cells == 0:
            return

        if "OrigID" in picked_mesh.cell_data:
            original_id = picked_mesh.cell_data["OrigID"][0]
            iz = original_id // (nr * nt)
            rem = original_id % (nr * nt)
            it = rem // nr
            ir = rem % nr
            state.update_selection(ir, it, iz)

    pl.enable_cell_picking(mesh=None, callback=on_cell_picked, show=False, 
                           show_message=False, through=False, use_hardware=False)

    btn_size = 80
    gap = 10
    
    x_col1 = 20
    x_col2 = x_col1 + btn_size + gap
    
    y_row1 = pl.window_size[1] - 120
    y_row2 = y_row1 - (btn_size + gap)
    y_row3 = y_row2 - (btn_size + gap)
    
    pl.add_checkbox_button_widget(lambda v: state.move_cursor(0, 0, 1), position=(x_col2, y_row1), 
                                  size=btn_size, color_on='grey', color_off='grey')
    pl.add_text("k++", position=(x_col2 + 25, y_row1 + 25), font_size=14, color='white')

    pl.add_checkbox_button_widget(lambda v: state.move_cursor(0, 0, -1), position=(x_col1, y_row1), 
                                  size=btn_size, color_on='grey', color_off='grey')
    pl.add_text("k--", position=(x_col1 + 25, y_row1 + 25), font_size=14, color='white')

    pl.add_checkbox_button_widget(lambda v: state.move_cursor(0, 1, 0), position=(x_col2, y_row2), 
                                  size=btn_size, color_on='grey', color_off='grey')
    pl.add_text("j++", position=(x_col2 + 25, y_row2 + 25), font_size=14, color='white')

    pl.add_checkbox_button_widget(lambda v: state.move_cursor(0, -1, 0), position=(x_col1, y_row2), 
                                  size=btn_size, color_on='grey', color_off='grey')
    pl.add_text("j--", position=(x_col1 + 25, y_row2 + 25), font_size=14, color='white')

    pl.add_checkbox_button_widget(lambda v: state.move_cursor(1, 0, 0), position=(x_col2, y_row3), 
                                  size=btn_size, color_on='grey', color_off='grey')
    pl.add_text("i++", position=(x_col2 + 25, y_row3 + 25), font_size=14, color='white')

    pl.add_checkbox_button_widget(lambda v: state.move_cursor(-1, 0, 0), position=(x_col1, y_row3), 
                                  size=btn_size, color_on='grey', color_off='grey')
    pl.add_text("i--", position=(x_col1 + 25, y_row3 + 25), font_size=14, color='white')

    state.update_selection(0, 0, 0)
    
    pl.show()
    pl.app.exec_()