from core_class.utils.find_vacuum_reluctance import find_vacuum_reluctance
from core_class.utils.extract_element_info import extract_element_info
from core_class.utils.find_element_dimension import find_element_dimension
from core_class.utils.find_minimum_reluctance import find_minimum_reluctance
from core_class.utils.find_magnet_source import find_magnet_source
from core_class.utils.find_element_segment_dimension_ratio import find_element_segment_dimension_ratio
from core_class.utils.find_winding_source import find_winding_source
from core_class.utils.find_total_magnetic_source import find_total_magnetic_source

class Element:
    def __init__(self,
                 motor = None,
                 position = None,
                 geometry = None,
                 mesh = None,
                 magnetic_potential = None,
                 winding_current = None):
        """
        Đối với các mảng (2x3) chứa nhiều thông tin, vị trí tương ứng:
        [     r_in    t_left     z_bot
              r_out   t_right    z_top    ]
        """

        self.position = position
        self.material_database = motor.material_database
        self.magnetic_potential = magnetic_potential
        self.winding_current = winding_current

        info = extract_element_info(position=position,
                                    geometry=geometry,
                                    mesh=mesh,
                                    )
        # material
        self.material = info.material

        # dimension
        self.dimension = info.dimension

        # dimension ratio
        self.dimension_ratio = find_element_segment_dimension_ratio(element= self).dimension_ratio

        # coordinate
        self.coordinate = info.coordinate

        # magnet properties
        self.segment_magnet_source = info.magnet_source
        self.magnetization_direction = info.magnetization_direction
        self.magnet_source = find_magnet_source(element= self).magnet_source

        # winding properties
        self.segment_winding_vector = info.winding_vector
        self.winding_normal = info.winding_normal
        self.element_winding_vector = None
        self.element_winding_vector = find_winding_source(element=self).element_winding_vector
        self.winding_source = find_winding_source(element=self).winding_source
        
        # total magnetic source 
        self.magnetic_source = find_total_magnetic_source(element=self).total_magnetic_source

        # define dimension
        dimension_calculated = find_element_dimension(coordinate=self.coordinate)
        self.length = dimension_calculated.length
        self.section_area = dimension_calculated.section_area

        # define vacuum reluctance
        self.vacuum_reluctance = find_vacuum_reluctance(length = self.length,
                                                        section_area = self.section_area).reluctance
        
        # define minimum reluctance
        self.minimum_reluctance = find_minimum_reluctance(element = self).reluctance

        # initialization for the first time
        self.reluctance = None
        self.flux_density = None
        self.flux_direct = None

        