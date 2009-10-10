import re

import mechanics
import game_state

#===============================================================#

class ArmorTemplate:
	def __init__(self, name, armor_type, dr, mob_penalty, coverage, conceal, mass, volume):
		self.name, self.armor_type, self.dr, self.mob_penalty, self.coverage, self.conceal, self.mass, self.volume = name, armor_type, dr, mob_penalty, coverage, conceal, mass, volume
		self.description = self.name

	def create_instance_at_location(self, location):
		global coverage_templates
		instance = mechanics.Armor(	location=location,name=self.name, slot_coverage=coverage_templates[self.coverage], concealment=self.conceal,
			description=self.description, armor_type=self.armor_type, damage_reduction=self.dr, mobility_penalty=self.mob_penalty)

#===============================================================#

class ClothingTemplate:
	def __init__(self, name, coverage, conceal, mass, volume):
		self.name, self.coverage, self.conceal, self.mass, self.volume = name, coverage, conceal, mass, volume
		self.description = self.name
	
	def create_instance_at_location(self, location):
		global coverage_templates
		instance = mechanics.Clothing(location=location,name=self.name, slot_coverage=coverage_templates[self.coverage], concealment=self.conceal, description=self.description)


#===============================================================#

class ConsumableTemplate:
	def __init__(self, name, effect, effect_rating):
		self.name = name

#===============================================================#

class GenericItemTemplate:
	def __init__(self, name, mass, volume):
		self.name, self.mass, self.volume = name, mass, volume
		self.description = self.name
	
	def create_instance_at_location(self, location):
		instance = terminal_game.Item(location=location, name=self.name, mass=self.mass, volume=self.volume, description=self.description)

#===============================================================#

class WeaponTemplate:
	def __init__(self, name, type, damage, special):
		self.name = name

#===============================================================#

class WearableContainerTemplate:
	def __init__(self, name, coverage, conceal, capacity, content_filter, mass, volume):
		self.name, self.coverage, self.conceal, self.capacity, self.content_filter, self.mass, self.volume = name, coverage, conceal, capacity, content_filter, mass, volume
		self.description = self.name
	
	def create_instance_at_location(self, location):
		global coverage_templates, content_filters
		instance = terminal_game.WearableContainer(	location=location,name=self.name, slot_coverage=coverage_templates[self.coverage], concealment=self.conceal,
			max_capacity=self.capacity, object_filters=content_filters[self.content_filter], description=self.description)

#===============================================================#

coverage_templates = {
	"Full":("head","forehead","right_eye","left_eye","nose","left_cheek","right_cheek","mouth","chin","neck_front","neck_back","chest","stomach","upper_back","lower_back","ass","groin","right_shoulder","right_bicep","right_elbow","right_forearm","right_wrist","right_hand","right_thigh","right_knee","right_shin","right_ankle","right_foot","left_shoulder","left_bicep","left_elbow","left_forearm","left_wrist","left_hand","left_thigh","left_knee","left_shin","left_ankle","left_foot"),
	"Shirt":("chest","stomach","upper_back","lower_back","right_shoulder","left_shoulder","right_bicep","left_bicep","right_elbow","left_elbow","right_forearm","left_forearm","left_wrist","right_wrist"),
	"Pants":("ass","groin","left_thigh","right_thigh","left_knee","right_knee","left_shin","right_shin","left_ankle","right_ankle"),
	"Vest":("chest","stomach","upper_back","lower_back"),
	"Shoes":("left_foot","right_foot"),
	"Backpack":("upper_back","lower_back"),
	"Gown":("chest","stomach","upper_back","lower_back","right_shoulder","left_shoulder","right_bicep","left_bicep","ass","groin","right_thigh","left_thigh"),
	"Nothing":(),
}

#===============================================================#

content_filters = {
	"Items":(),
}

standard_tables = {
#===============================================================#

ArmorTemplate:[	["name",	"armor_type",	"dr",	"mob_penalty",	"coverage",	"conceal",	"mass",	"volume"	],
	["Salvager Suit Mk1",	"Soft",	"16",	"6",	"Full",	"1.0",	"80.0",	"50.0"	],
	["Leather Vest",	"Soft",	"2",	"0",	"Vest",	"0.5",	"0.35",	"0.50"	],
	["Leather Shirt",	"Soft",	"2",	"0",	"Shirt",	"1.0",	"0.25",	"0.15"	],
	["Leather Pants",	"Soft",	"2",	"0",	"Pants",	"1.0",	"0.35",	"0.25"	],
	["Chain Shirt",	"Soft",	"6",	"2",	"Shirt",	"0.8",	"5.00",	"1.25"	],
	["Chain Pants",	"Soft",	"6",	"2",	"Pants",	"0.8",	"6.00",	"1.75"	]],

#===============================================================#

ClothingTemplate:[	["name",	"coverage",	"conceal",	"mass",	"volume"	],
	["Linen Shirt",	"Shirt",	"1.0",	"0.35",	"0.50"	],
	["Linen Pants",	"Pants",	"1.0",	"0.75",	"1.00"	],
	["Leather Shoes",	"Shoes",	"0.8",	"1.00",	"1.50"	],
	["Hospital Gown",	"Gown",	"0.8",	"0.50",	"0.50"	],
	["Slippers",	"Shoes",	"0.5",	"0.50",	"0.50"	],
	],

#===============================================================#

ConsumableTemplate:[	["name",	"effect",	"effect_rating"	],
	["Healing Potion",	"heal",	"2"	],
	["Bread",	"food",	"5"	],
	["Antidote",	"cure",	"1"	]],

#===============================================================#

GenericItemTemplate:[	["name",	"mass",	"volume"],
	["Sheet of Leather",	"0.5",	"1.0"],
	["Leather Cord",	"0.1",	"0.25"],
	["Steel Rivets",	"0.2",	"0.1"]],
	

#===============================================================#

WeaponTemplate:[	["name",	"type",	"damage",	"special"	],
	["Long Sword",	"Sword",	"2d8",	"Versatile"	],
	["Great Sword",	"Sword",	"2d10",	"Two-Handed"	],
	["Short Sword",	"Sword",	"2d6",	"Light"	],
	["Warhammer",	"Hammer",	"2d8",	"Versatile"	],
	["Greathammer",	"Hammer",	"2d10",	"Two-Handed"	],
	["Light Mace",	"Hammer",	"2d6",	"Light"	]],

#===============================================================#

WearableContainerTemplate:[	["name",	"coverage",	"conceal",	"capacity",	"content_filter",	"mass",	"volume"	],
	["Backpack",	"Backpack",	"1.0",	"10.0",	"Items",	"0.5",	"10.0"	],
	["Pouch",	"Nothing",	"1.0",	"2.5",	"Items",	"0.25",	"2.5"	],
	["Satchel",	"Nothing",	"1.0",	"10.0",	"Items",	"0.5",	"10.0"	]],

#===============================================================#

}

#===============================================================#

standard_descriptions = {
	"Hospital Gown":	"Not exactly fashionable, but at least it covers you.",
	"Slippers":	"Simple slippers to keep your feet warm.",
	"Salvager Suit Mk1":	"This full-body armored suit is certified for operation in most hostile conditions, including vacuum and radiation hazards. It provides integral communications and life-support equipment as well as numerous attachment points for useful equipment. It is one of the most common suits of its type and sees use on most salvage ships.",
	"Linen Pants":	"These plain pants are quite comfortable, but otherwise unremarkable.",
	"Linen Shirt":	"This is a plain white shirt made of linen. It is loose-fitting and comfortable.",
	"Leather Shoes":	"Soft leather on top, hard leather on the bottom; these shoes are quit popular among those with feet.",
	"Leather Vest":	"This vest is made of tough leather and protects the front and back of the torso.",
}

#===============================================================#

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

turn_tables_into_templates(standard_tables, standard_descriptions)

#===============================================================#

area_prototypes =	[
	["name",	"map_name",	"map_coords",	"area_id",	"description_id"	],
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
	]

map_files =	{
	"citadel_cryo_wing":	"citadel_cryo_wing.png",
	}

area_descriptions =	{
	"citadel_cryo_recovery_a":	"This small room is well-lit and smells of sanitized air. A huge machine dominates one half of the room; the cryonic recovery module responsible for restoring frozen bodies to life. The rest of the room is decorated with various medical devices related to the thawing process. There are two ways out; a door marked 'Supplies' and another marked 'Recovery Suite'",
	"citadel_cryo_recovery_b":	"This small room is home to the second of two cryonic recovery modules on the station. Unfortunately, the module seems to have failed. The room smells faintly of burned meat and ozone. The medical equipment here is obviously damaged. A severely burned corpse lies in the middle of the floor.",
	"small_supply_room":	"Barely larger than a walk-in closet, this supply room is lined on all four walls with shelves from floor to ceiling. There is one exit; the door you came in through.",
	}

prop_placement_table =	[
	["location",	"name",	"prop_id",	"description"],
	["citadel_cryo_recovery_b",	"Burned Corpse",	"cryo_fail_corpse",	"The corpse of a male human, probably young adult. It's lying face down on the floor, naked. The body is covered from head to toe in severe burns; it appears they may have been inflicted by a malfunction in the cryo recovery module. Death was not immediate; from the position of the body, it looks like he passed away after crawling several meters across the floor. Curiously, it looks as if he was crawling toward the supply room rather than the recovery suite."],
	["citadel_cryo_recovery_b",	"Damaged Equipment",	"cryo_fail_equipment",	"Most of the equipment in this room, including the recovery module itself, has been severely damaged. It looks like some sort of power surge blew out most of the equipment and started several small fires. Upon further investigation, you find that someone has modified the main power conduit for this room. The modification probably caused the surge but it's impossible to say whether it was sabotage or just incompetence."],
	["citadel_cryo_recovery_b_supply_room",	"Unusual Container",	"cryo_fail_box",	"This container stands out from the various medical supplies in the room. Unfortunately, it seems to be sealed shut and is too heavy to move by hand."],
	]

item_placement_table =	[
	["location",	"template_list"	],
	["citadel_cryo_recovery_a_supply_room",	"Steel Ricets"	],
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
	"std_door":	("Door",	"This is a standard air-tight automatic door controlled by motion sensors. Most star ships and space stations use a variation on this design due to its combination safety and convenience. Such doors are almost always controlled by a central network of some kind so that they can be remotely opened or closed. The door seems to be locked in the open position; the status lights above it indicate that this is because a general evacuation order is in place."),
	}
	
def create_item_at_location(item_name, location_id):
	pass
	#global full_item_dict, full_area_dict
	#full_item_dict[item_name].create_instance_at_location(full_area_dict[location])

def fill_new_game_in_target_state(target_state):
	target_state.area_dict = {}
	area_args = area_prototypes[0]
	for area_proto in area_prototypes[1:]:
		params = dict(zip(area_args, area_proto))
		
		name = params["name"]
		
		if params["description_id"] == None:
			params["description_id"] = params["area_id"]
		
		area = mechanics.Area(name = name, area_identifier=params["area_id"], description=area_descriptions.get(params["description_id"]))
		
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
#	Leader of the Command staff aboard the Adversity, Captain John Haskell is
#	a stern man. His younger years were spent in the Navy; he had a successful
#	military career in which he eventually captained a destroyer-class star
#	ship during the Martian Secession	wars. At the end of end of the war, he
#	retired from the navy with honors. Although he might have lived a peaceful
#	life on Earth, he decided to take a job offer with the non-profit Free
#	Information Society. He was eventually put in command of a star ship once
#	again; the FIS Adversity python-class research vessel. His crew describe
#	him as harsh and distant, and many question the wisdom of putting an
#	ex-military captain in charge of a research vessel. None can deny, however,
#	that he is good at what he does and keeps the crew in line without damaging
#	their morale. He's not open about his motivations for joining the FIS, but
#	he seems driven by his work in a way that few others are. Some suggest,
#	when the captain is out of earshot, that he sees his work for the FIS as
#	some sort of penance for something that happened during the war. The only
#	person who knows for sure is Haskell.
#
# 2) Chief Engineer Fortran, Male, 36
#	A close personal friend of Captain Haskell, Chief Engineer Dennis Fortran once served in the Marines. Haskell and Fortran met
#	during a particularly protracted campaign during the Martian Secession wars. Sergeant Major Fortran, as he was known at the time,
#	was among the marines stationed aboard Haskell's ship. In one particularly nasty battle, the marine garrison and command center
#	were breached by enemy fire; half the batallion and the entire command section were lost. As the highest-ranked enlisted marine
#	left, Fortran assumed command of the remaining marines and worked alongisde Haskell during the difficult months that followed.
#	By the time the ship reached safety, Fortran had been severely wounded. Although he survived, he lost the use of his left arm and
#	was honorably discharged from the marine corps. He eventually enrolled at the prestigious Lunar Academy and completed degrees
#	in Mechanical and Astronautical Engineering. During that time, he also underwent experimental surgery to replace his lost arm
#	with a bionic substitute. With his new knowledge and the use of his arm restored, he initially planned te re-enlist; he changed
#	his plans suddenly when Haskell contacted him. He doesn't discuss what Haskell told him, but he signed on as Chief Engineer of
#	the Adversity shortly thereafter.
#
# 3) Science Officer Erlang, Female, 25
#
# 4) Security Officer Pascal, Female, 28
#
# 5) Specialist Ajax, Male, 29
#
# 6) Specialist Perl, Female, 22
