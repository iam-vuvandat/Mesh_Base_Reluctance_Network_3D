import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def plot_tetrahedron_matplotlib():
    # 1. Định nghĩa 4 đỉnh của tứ diện đều
    # Cách đơn giản nhất để tạo tứ diện đều là dùng các góc của một hình lập phương
    vertices = np.array([
        [1, 1, 1],
        [1, -1, -1],
        [-1, 1, -1],
        [-1, -1, 1]
    ], dtype=float)

    # 2. Định nghĩa các mặt (faces)
    # Mỗi mặt là một tam giác nối 3 đỉnh.
    # Chúng ta sử dụng chỉ số (index) của các đỉnh trong mảng `vertices` ở trên.
    faces = [
        [vertices[0], vertices[1], vertices[2]],
        [vertices[0], vertices[1], vertices[3]],
        [vertices[0], vertices[2], vertices[3]],
        [vertices[1], vertices[2], vertices[3]]
    ]

    # 3. Khởi tạo đồ thị 3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # 4. Tạo đối tượng Poly3DCollection để vẽ các mặt
    # alpha là độ trong suốt (0.0 - 1.0)
    mesh = Poly3DCollection(faces, alpha=0.6, facecolor='cyan', edgecolor='k')
    ax.add_collection3d(mesh)

    # 5. Căn chỉnh trục để hình không bị méo
    # Matplotlib 3D cần mẹo này để tỉ lệ các trục bằng nhau
    x, y, z = vertices[:,0], vertices[:,1], vertices[:,2]
    max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max() / 2.0
    mid_x = (x.max()+x.min()) * 0.5
    mid_y = (y.max()+y.min()) * 0.5
    mid_z = (z.max()+z.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    # Đặt nhãn và tiêu đề
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.title("Tứ diện đều với Matplotlib")

    plt.show()

if __name__ == "__main__":
    plot_tetrahedron_matplotlib()