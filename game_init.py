import content

import game_state

content.fill_new_game_in_target_state(game_state.current_state)
game_state.current_state.focus_on_marker(game_state.current_state.get_marker_for_identifier("citadel_cryo_recovery_a"))

initial_commands = ["area_description",]

def pulse_update():
	pass

