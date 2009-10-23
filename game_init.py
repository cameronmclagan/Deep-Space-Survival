import xml_content_loader

import game_state

xml_content_loader.fill_target_state_from_file_list(game_state.current_state, ["./data/cryo_wing.xml"])
game_state.current_state.focus_on_marker(game_state.current_state.get_marker_for_identifier("cryo_recovery_a"))

initial_commands = ["area_description",]

def pulse_update():
	pass

