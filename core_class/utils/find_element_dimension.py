import numpy as np 
from dataclasses import dataclass
from typing import Any

@dataclass
class Output:
    length :Any
    section_area : Any 

def find_element_dimension(coordinate):
    # extract dimension: 
    r_in = coordinate[0,0]
    r_out = coordinate[1,0]
    theta_right = coordinate[0,1]
    theta_left  = coordinate[1,1]
    z_bottom = coordinate[2,0]
    z_top = coordinate[2,1]

    # create empty array 
    length = np.zeros((2,3)) # [lrin,ltleft,lzbot;lrout,ltright,lztop]
    section_area = np.zeros((2,3)) # [Srin,Stleft,Szbot;Srout,Stright,Sztop]

    # find dimension
    open_angle = np.abs((theta_right - theta_left))
    half_open = open_angle / 2
    length[0,0] = (1/2) * ( 1+ np.cos(half_open) ) * np.abs((r_in - (1/2 * (r_out + r_in))))
    length[1,0] = (1/2) * ( 1+ np.cos(half_open) ) * np.abs((r_out - (1/2 * (r_out + r_in))))

    length[0,1] = (1/2) * (np.sin(half_open)) * (r_in + r_out)
    length[1,1] = length[0,1]

    length[0,2] = np.abs((z_bottom - z_top)/2)
    length[1,2] = length[0,2]

    section_area[0,0] = (length[0,2] + length[1,2]) * np.sin(half_open) * (3/2 * r_in + 1/2 * r_out)
    section_area[1,0] = (length[0,2] + length[1,2]) * np.sin(half_open) * (1/2 * r_in + 3/2 * r_out)

    section_area[0,1] = (length[0,2] + length[1,2]) * (1/2) * (r_out + r_in) * (1 + np.cos(half_open))
    section_area[1,1] = section_area[0,1] 

    section_area[0,2] = (r_out * np.cos(half_open) * r_out * np.sin(half_open)) - (r_in * np.cos(half_open) * r_in * np.sin(half_open)) 
    section_area[1,2] = section_area[0,2]

    return Output(length= length,
                  section_area= section_area)