import xml_content_loader

import game_state

xml_content_loader.fill_current_state_from_file_list( ["./data/weapons.xml","./data/cryo_wing.xml"])
game_state.current_state.focus_on_marker("cryo_recovery_a")

initial_commands = ["area_description",]

def pulse_update():
	pass

