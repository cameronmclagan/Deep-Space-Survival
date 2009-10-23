import re

import mechanics
import game_state

#===============================================================#
class AreaTemplate:
	pass

class AreaInstance:
	pass


template_tables = {
#===============================================================#

AreaTemplate:	[
	["name",					"dimensions",	"desc_id",	"floor_type",	"wall_type", 		"ceiling_type", "integral_objects"],
	["Cryo Recovery Module",	(5,5),			None,		"safety_panel",	"cryo_wing_wall",	("Rec],
	["Medical Recovery Suite",	],
	["Cryonics General Care",	],
	["Cryo Patient Prep",		],
	["Pre-Freeze Ward",			],
	["Cryo Doctor Prep",		],
	["Operating Room",			],
	["Cryo Freezer",			],
	["Cryo Wing Lobby",			],
	["Small Supply Room",		],
	["Medium Supply Room",		],
	["Physical Therapy Center",	],
	["Counseling Office",		],
	],

}

#===============================================================#

template_description_tables = {
	"Salvager Suit Mk1":	"This full-body armored suit is certified for operation in most hostile conditions, including vacuum and radiation hazards. It provides integral communications and life-support equipment as well as numerous attachment points for useful equipment. It is one of the most common suits of its type and sees use on most salvage ships.",
}

#===============================================================#

instance_tables = {
AreaInstance:	[
	["name",	"map_name",	"map_coords",	"area_id",	"desc_id",	"network_path",	"utility_section",	"life_support_section"],
	["Cryo Recovery A",	"citadel_cryo_wing",	(0.38,0.90),	"citadel_cryo_recovery_a",	None	],
	["Cryo Recovery B",	"citadel_cryo_wing",	(0.62,0.90),	"citadel_cryo_recovery_b",	None	],
	["Supply Room",	"citadel_cryo_wing",	(0.27,0.88),	"citadel_cryo_recovery_a_supply_room",	"small_supply_room"	],
	["Supply Room",	"citadel_cryo_wing",	(0.73,0.88),	"citadel_cryo_recovery_b_supply_room",	"small_supply_room"	],
	["Cryo Recovery Suite",	"citadel_cryo_wing",	(0.50,0.77),	"citadel_cryo_recovery_suite",	None	],
	["Supply Room",	"citadel_cryo_wing",	(0.50,0.90),	"citadel_cryo_recovery_suite_supply_room",	"medium_supply_room"	],
	["Cryonics General Care",	"citadel_cryo_wing",	(0.50,0.62),	"citadel_cryo_general_care",	None	],
	["Pre-Freeze Ward A",	"citadel_cryo_wing",	(0.27,0.62),	"citadel_cryo_pre_freeze_a",	None	],
	["Pre-Freeze Ward B",	"citadel_cryo_wing",	(0.73,0.62),	"citadel_cryo_pre_freeze_b",	None	],
	["Cryo Patient Prep A",	"citadel_cryo_wing",	(0.08,0.62),	"citadel_cryo_patient_prep_a",	None	],
	["Cryo Patient Prep B",	"citadel_cryo_wing",	(0.93,0.62),	"citadel_cryo_patient_prep_b",	None	],
	["Cryo Doctor Prep A",	"citadel_cryo_wing",	(0.27,0.77),	"citadel_cryo_doctor_prep_a",	None	],
	["Cryo Doctor Prep B",	"citadel_cryo_wing",	(0.73,0.77),	"citadel_cryo_doctor_prep_b",	None	],
	["Operating Room A",	"citadel_cryo_wing",	(0.38,0.90),	"citadel_cryo_operating_room_a",	None	],
	["Operating Room B",	"citadel_cryo_wing",	(0.38,0.90),	"citadel_cryo_operating_room_b",	None	],
	["Cryo Freezer A",	"citadel_cryo_wing",	(0.38,0.90),	"citadel_cryo_freezer_a",	None	],
	["Cryo Freezer B",	"citadel_cryo_wing",	(0.38,0.90),	"citadel_cryo_freezer_a",	None	],
	["Cryo Wing Lobby",	"citadel_cryo_wing",	(0.38,0.90),	"citadel_cryo_lobby",	None	],
	["Physical Therapy Center",	"citadel_cryo_wing",	(0.38,0.90),	"citadel_cryo_physical_therapy",	None	],
	["Post-Cryo Counseling Office",	"citadel_cryo_wing",	(0.38,0.90),	"citadel_cryo_counseling_office",	None	],
	],
}

instance_description_tables = {

}

full_item_dict = {}

def turn_tables_into_templates(tables, descriptions):
	global full_item_dict
	for type, table in tables.items() :
		headings = table[0]
		for line in table[1:]:
			args = dict(zip(headings,line))
			template = type(**args)
			if template.name in descriptions:
				template.description = template.name + "\n" + descriptions[template.name]
			full_item_dict[template.name] = template

#===============================================================#


map_files =	{
	"citadel_cryo_wing":	"citadel_cryo_wing.png",
	}

area_descriptions =	{
	"citadel_cryo_recovery_a":	"This small room is well-lit and smells of sanitized air. A huge machine dominates one half of the room; the cryonic recovery module responsible for restoring frozen bodies to life. The rest of the room is decorated with various medical devices related to the thawing process. There are two ways out; a door marked 'Supplies' and another marked 'Recovery Suite'.",
	"citadel_cryo_recovery_b":	"This small room is home to the second of two cryonic recovery modules on the station. Unfortunately, the module seems to have failed. The room smells faintly of burned meat and ozone. The medical equipment here is obviously damaged. A severely burned corpse lies in the middle of the floor.",
	"small_supply_room":	"Barely larger than a walk-in closet, this supply room is lined on all four walls with shelves from floor to ceiling. There is one exit; the door you came in through.",
	}

prop_placement_table =	[
	["location",	"name",	"prop_id",	"description"],
	["citadel_cryo_recovery_b",	"Burned Corpse",	"cryo_fail_corpse",	"The corpse of a male human, probably young adult. It's lying face down on the floor, naked. The body is covered from head to toe in severe burns; it appears they may have been inflicted by a malfunction in the cryo recovery module. Death was not immediate; from the position of the body, it looks like he passed away after crawling several meters across the floor. Curiously, it looks as if he was crawling toward the supply room rather than the recovery suite."],
	["citadel_cryo_recovery_b",	"Damaged Equipment",	"cryo_fail_equipment",	"Most of the equipment in this room, including the recovery module itself, has been severely damaged. It looks like some sort of power surge blew out most of the equipment and started several small fires. Upon further investigation, you find that someone has modified the main power conduit for this room. The modification probably caused the surge but it's impossible to say whether it was sabotage or just incompetence."],
	["citadel_cryo_recovery_b_supply_room",	"Unusual Container",	"cryo_fail_box",	"This container stands out from the various medical supplies in the room. Unfortunately, it seems to be sealed shut and is too heavy to move by hand."],
	["citadel_cryo_recovery_a_supply_room",	"Box marked 'Nutri-Pak'",	"24xNutri-Pak", "cryo_start_food_box",	"This shoebox-sized plastic container is marked 'Nutri-Pak'. The writing on the outside claims that it contains two dozen 250ml packages of 'nutrient gel'."],
	]

container_placement_table =	[
	["location",	"container_type",	"container_id"],
	]	

item_placement_table =	[
	["location",	"template_list"	],
	["citadel_cryo_recovery_a_supply_room",	"Steel Rivets"	],
	]

portal_prototypes =	[
	["type",	"location",	"destination",	"double_ended"	],
	["std_door",	"citadel_cryo_recovery_a",	"citadel_cryo_recovery_suite",	True	],
	["std_door",	"citadel_cryo_recovery_a",	"citadel_cryo_recovery_a_supply_room",	True	],
	["std_door",	"citadel_cryo_recovery_b",	"citadel_cryo_recovery_suite",	True	],
	["std_door",	"citadel_cryo_recovery_b",	"citadel_cryo_recovery_b_supply_room",	True	],
	["std_door",	"citadel_cryo_recovery_suite",	"citadel_cryo_recovery_suite_supply_room",	True	],
	["std_door",	"citadel_cryo_recovery_suite",	"citadel_cryo_general_care",	True	],
	["std_door",	"citadel_cryo_general_care",	"citadel_cryo_pre_freeze_a",	True	],
	["std_door",	"citadel_cryo_general_care",	"citadel_cryo_pre_freeze_b",	True	],
	]

portal_type_descriptions =	{
#	"type":	("name",	"description"),
	"std_door":	("Door",	),
	}
	
def create_item_at_location(item_name, location_id):
	pass
	#global full_item_dict, full_area_dict
	#full_item_dict[item_name].create_instance_at_location(full_area_dict[location])

def fill_new_game_in_target_state(target_state):
	pass

def hiding_place():
	target_state.area_dict = {}
	area_args = area_prototypes[0]
	for area_proto in area_prototypes[1:]:
		params = dict(zip(area_args, area_proto))
		
		name = params["name"]
		
		if params["desc_id"] == None:
			params["desc_id"] = params["area_id"]
		
		area = mechanics.Area(name = name, area_identifier=params["area_id"], description=area_descriptions.get(params["desc_id"]))
		
		target_state.area_dict[params["area_id"]] = area
		
		area_marker = target_state.get_marker_for_identifier(params["area_id"])
		area.marker = area_marker
		
		area_marker.object = area
		area_marker.focus_commands = mechanics.area_commands
		area_marker.add_keys_on_focus = ("been_to_%s" % params["area_id"],)

	prop_args = prop_placement_table[0]
	for prop_def in prop_placement_table[1:]:
		params = dict(zip(prop_args, prop_def))
		
		prop = mechanics.Item(location=target_state.area_dict[params["location"]],name=params["name"],description=params["description"])
	
	portal_args = portal_prototypes[0]
	for portal_proto in portal_prototypes[1:]:
		params = dict(zip(portal_args, portal_proto))
		
		location = target_state.area_dict[params["location"]]
		destination = target_state.area_dict[params["destination"]]
		double_ended = bool(params["double_ended"])
		
		location_marker = target_state.get_marker_for_identifier(params["location"])
		destination_marker = target_state.get_marker_for_identifier(params["destination"])
		
		type_name, type_description = portal_type_descriptions[params["type"]]
		
		name = type_name + " to " + destination.name
		portal = mechanics.Item(name=name, location=location, description=type_description)
		
		move_target_marker = target_state.new_marker_for_identifier(portal.unique_name + "_move_target", visible_name=destination.formatted_name, destination=destination_marker, location=location_marker)

		if double_ended :
			name = type_name + " to " + location.name
			portal = mechanics.Item(name=name, location=destination, description=type_description)
			
			move_target_marker = target_state.new_marker_for_identifier(portal.unique_name + "_move_target", visible_name=location.formatted_name, destination=location_marker, location=destination_marker)

	
#====================#
# Premade Characters #
#====================#
#
# 1) Captain Haskell, Male, 48
#    Leader of the Command staff aboard the Adversity, Captain John Haskell is
#    a stern man. His younger years were spent in the Navy; he had a successful
#    military career in which he eventually captained a destroyer-class star
#    ship during the Martian Secession wars. At the end of end of the war, he
#    retired from the navy with honors. Although he might have lived a peaceful
#    life on Earth, he decided to take a job offer with the non-profit Free
#    Information Society. He was eventually put in command of a star ship once
#    again; the FIS Adversity python-class research vessel. His crew describe
#    him as harsh and distant, and many question the wisdom of putting an
#    ex-military captain in charge of a research vessel. None can deny, however,
#    that he is good at what he does and keeps the crew in line without damaging
#    their morale. He's not open about his motivations for joining the FIS, but
#    he seems driven by his work in a way that few others are. Some suggest,
#    when the captain is out of earshot, that he sees his work for the FIS as
#    some sort of penance for something that happened during the war. The only
#    person who knows for sure is Haskell.
#
# 2) Chief Engineer Fortran, Male, 36
#    A close personal friend of Captain Haskell, Chief Engineer Dennis Fortran
#    once served in the Marines. Haskell and Fortran met during a particularly
#    protracted campaign during the Martian Secession wars. Sergeant Major
#    Fortran, as he was known at the time, was among the marines stationed
#    aboard Haskell's ship. In one particularly nasty battle, the marine
#    garrison and command center were breached by enemy fire; half the batallion
#    and the entire command section were lost. As the highest-ranked enlisted
#    marine left, Fortran assumed command of the remaining marines and worked
#    alongisde Haskell during the difficult months that followed. By the time
#    the ship reached safety, Fortran had been severely wounded. Although he
#    survived, he lost the use of his left arm and was honorably discharged from
#    the marine corps. He eventually enrolled at the prestigious Lunar Academy
#    and completed degrees in Mechanical and Astronautical Engineering. During
#    that time, he also underwent experimental surgery to replace his lost arm
#    with a bionic substitute. With his new knowledge and the use of his arm
#    restored, he initially planned te re-enlist; he changed his plans suddenly
#    when Haskell contacted him. He doesn't discuss what Haskell told him, but
#    he signed on as Chief Engineer of the Adversity shortly thereafter.
#
# 3) Science Officer Erlang, Female, 25
#
# 4) Security Officer Pascal, Female, 28
#
# 5) Specialist Ajax, Male, 29
#
# 6) Specialist Perl, Female, 22
