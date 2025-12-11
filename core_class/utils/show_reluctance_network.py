import numpy as np
import pyvista as pv

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
        if "iron" in mat_name or "steel" in mat_name: mat_ids[idx] = 1
        elif "magnet" in mat_name:                    mat_ids[idx] = 2
        elif "coil" in mat_name or "winding" in mat_name: mat_ids[idx] = 3
        else:                                         mat_ids[idx] = 0
    
    grid_pv.cell_data["MatID"] = mat_ids

    pv.set_plot_theme("dark")
    pl = pv.Plotter(window_size=[2560, 1440]) 
    pl.set_background("#050505") 
    pl.add_axes()
    
    try:
        pl.enable_anti_aliasing('ssaa')
    except: pass

    styles = {
        0: ("Air",    "#333333", 0.4), 
        1: ("Iron",   "#F0F0F0", 0.9), 
        2: ("Magnet", "#FF3333", 0.9), 
        3: ("Coil",   "#FFAA00", 0.9)  
    }

    for mat_id, (label, color, opacity) in styles.items():
        sub_mesh = grid_pv.threshold([mat_id, mat_id], scalars="MatID", preference="cell")
        if sub_mesh.n_cells > 0:
            edge_color = "#222222" if mat_id == 0 else "#555555"
            pl.add_mesh(sub_mesh, color=color, opacity=opacity, 
                        show_edges=True, edge_color=edge_color, label=label,
                        pickable=True)

    instructions = "CONTROLS\nw / s : Radius\nd / a : Theta\nr / f : Axial\nt     : Toggle Text"
    pl.add_text(instructions, position='upper_right', font_size=10, color='white', font='courier')
    pl.add_legend(bcolor='#1A1A1A', border=True, size=(0.15, 0.15), loc='lower right', face='rectangle')

    class ViewerState:
        def __init__(self):
            self.selected_idx = None 
            self.highlight_actor = None 
            self.info_actor = None 
            self.show_text = True 

        def update_selection(self, ir, it, iz):
            if not (0 <= ir < nr and 0 <= it < nt and 0 <= iz < nz): return 

            self.selected_idx = (ir, it, iz)
            flat_id = ir + it * nr + iz * (nr * nt)
            
            if self.highlight_actor:
                pl.remove_actor(self.highlight_actor)
            
            try:
                cell_geo = grid_pv.extract_cells([flat_id])
                self.highlight_actor = pl.add_mesh(cell_geo, style='wireframe', color='#00FFFF', 
                                                    line_width=4, render=False, name="highlight")
            except: pass

            if self.info_actor:
                pl.remove_actor(self.info_actor)

            if not self.show_text:
                pl.render()
                return

            element_obj = elements_matrix[ir, it, iz]
            
            info_str = f"SELECTED ELEMENT\nIdx: [{ir}, {it}, {iz}] | ID: {flat_id}\n" + "="*30 + "\n\n"
            
            if element_obj is None:
                info_str += "Status: Empty"
            else:
                attrs = vars(element_obj)
                for key, val in attrs.items():
                    if key == "dimension" and isinstance(val, np.ndarray):
                        info_str += "Dimension (2x3) [r, theta, z]:\n"
                        info_str += f"  El : [{val[0,0]:.6f}, {val[0,1]:.6f}, {val[0,2]:.6f}]\n"
                        info_str += f"  Seg: [{val[1,0]:.6f}, {val[1,1]:.6f}, {val[1,2]:.6f}]"
                    
                    elif key == "coordinate" and isinstance(val, np.ndarray):
                        info_str += "Coordinate (2x3) [r, theta, z]:\n"
                        info_str += f"  Start: [{val[0,0]:.6f}, {val[0,1]:.6f}, {val[0,2]:.6f}]\n"
                        info_str += f"  End  : [{val[1,0]:.6f}, {val[1,1]:.6f}, {val[1,2]:.6f}]"
                    
                    elif isinstance(val, float): 
                        info_str += f"{key}: {val:.6f}"
                    
                    elif isinstance(val, np.ndarray):
                        arr_str = np.array2string(val.flatten(), precision=6, separator=', ')
                        info_str += f"{key}:\n{arr_str}"

                    elif key in ['mesh', 'motor', 'geometry']: 
                        info_str += f"{key}: <Ref Object>"
                    
                    else: 
                        info_str += f"{key}: {val}"
                    
                    info_str += "\n\n"
            
            self.info_actor = pl.add_text(info_str, position='upper_left', font_size=11, 
                                        color='white', font='courier', name='hud_info')
            pl.render()

        def toggle_text(self):
            self.show_text = not self.show_text
            if not self.show_text:
                if self.info_actor:
                    pl.remove_actor(self.info_actor)
                pl.render()
            else:
                if self.selected_idx:
                    self.update_selection(*self.selected_idx)

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

    def move_cursor(dr, dt, dz):
        if state.selected_idx is None:
            state.update_selection(0, 0, 0)
        else:
            r, t, z = state.selected_idx
            state.update_selection(r + dr, t + dt, z + dz)

    pl.add_key_event("w", lambda: move_cursor(1, 0, 0))   
    pl.add_key_event("s", lambda: move_cursor(-1, 0, 0))  
    pl.add_key_event("d", lambda: move_cursor(0, 1, 0))   
    pl.add_key_event("a", lambda: move_cursor(0, -1, 0))  
    pl.add_key_event("r", lambda: move_cursor(0, 0, 1))   
    pl.add_key_event("f", lambda: move_cursor(0, 0, -1)) 
    pl.add_key_event("t", state.toggle_text)

    pl.view_isometric()
    pl.show()