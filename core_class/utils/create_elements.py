from core_class.models.Element import Element
import numpy as np 
from tqdm import tqdm  # Thêm thư viện tqdm

def create_elements(motor, debug=True):
    """
    Tạo mảng 3D các đối tượng Element.
    Nếu debug=True, hiển thị thanh tiến trình.
    """
    
    # Lấy kích thước lưới
    nr = int(motor.mesh.n_cells_r)
    nt = int(motor.mesh.n_cells_t)
    nz = int(motor.mesh.n_cells_z)
    
    # Tính tổng số phần tử để tqdm biết khi nào chạy xong (để tính % và ETA)
    total_elements = nr * nt * nz
    
    # Khởi tạo mảng chứa object
    elements = np.empty((nr, nt, nz), dtype=object)
    
    # In thông báo nếu đang debug
    if debug:
        print(f"[INFO] Creating {total_elements} elements...")

    # Sử dụng tqdm với tham số 'disable':
    # - Nếu debug = True -> disable = False -> Hiện thanh tiến trình
    # - Nếu debug = False -> disable = True -> Ẩn thanh tiến trình
    with tqdm(total=total_elements, desc="Initializing Elements", disable=not debug) as pbar:
        for i_r in range(nr):
            for i_t in range(nt):
                for i_z in range(nz):
                    position = (i_r, i_t, i_z)
                    
                    # Khởi tạo Element
                    elements[i_r, i_t, i_z] = Element(
                        position=position,
                        motor=motor,
                        geometry=motor.geometry,
                        mesh=motor.mesh
                    )
                    
                    # Cập nhật thanh tiến trình thêm 1 đơn vị
                    pbar.update(1)
    
    return elements