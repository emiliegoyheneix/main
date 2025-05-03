struct ExtractMorph
(
	skin_obj = undefined,
	intermediate_object = undefined,
	target_obj = undefined,
	result_obj = undefined,
	result_name = "Extract_Morph",
	index = undefined,
	
	vertcount = undefined,
	modified_verts = #(),
	
	skin_points = #(),
	target_points = #(),
	intermediate_points = #(),
	result_points = #(),
	
	complete = false,
	
	fn create_obj =
	(
		intermediate_object = copy skin_obj
		result_obj = copy skin_obj name:(uniqueName(result_name))
		result_name = "Extract_Morph"
		update intermediate_object
		update result_obj
	),
	
	fn find_skin_mod =
	(
		index = undefined
		for i=1 to intermediate_object.modifiers.count do
		(
			if classOf intermediate_object.modifiers[i] == Skin then
			(
				index = i
			)
		)
	),
	
	fn delete_mod obj all:false=
	(
		index_mod = index
		if all == false then
		(
			index_mod = index-1
		)
		maxOps.CollapseNodeTo obj (index+1) true
		for i=1 to index_mod do
		(
			deleteModifier obj 1
		)
	),

	fn get_vertcount =
	(
		vertcount = undefined
		skin_obj_vertcount = polyop.getNumVerts skin_obj
		target_obj_vertcount = polyop.getNumVerts target_obj
		if skin_obj_vertcount == target_obj_vertcount then
		(
			vertcount = skin_obj_vertcount
		)
	),

	fn get_vertices_moved =
	(
		modified_verts = #()
		for vert=1 to vertcount do
		(
			s_pos = in coordsys #local polyop.getVert skin_obj vert
			m_pos = in coordsys #local polyop.getVert target_obj vert
			
			if s_pos != m_pos then
			(
				append modified_verts vert
			)
		)
	),
	
	fn get_pos_vert =
	(
		skin_points = #()
		target_points = #()
		intermediate_points = #()
		result_points = #()
		for vert in modified_verts do
		(
			skinPoint = in coordsys #local polyOp.getVert skin_obj vert
			targetPoint = in coordsys #local polyOp.getVert target_obj vert
			intermediatePoint = in coordsys #local polyOp.getVert intermediate_object vert
			resultPoint = in coordsys #local polyOp.getVert result_obj vert

			append skin_points skinPoint
			append target_points targetPoint
			append intermediate_points intermediatePoint
			append result_points resultPoint
		)
	),
	
	fn find_offsets =
	(
		for vert, count in modified_verts do
		(
			x_array = #((intermediate_points[count][1] + 1), intermediate_points[count][2], intermediate_points[count][3])
			y_array = #(intermediate_points[count][1], (intermediate_points[count][2] + 1), intermediate_points[count][3])
			z_array = #(intermediate_points[count][1], intermediate_points[count][2], (intermediate_points[count][3] + 1))

			in coordsys skin_obj polyOp.setVert intermediate_object vert [x_array[1], x_array[2], x_array[3]]
			x_point_array = in coordsys skin_obj polyOp.getVert skin_obj vert
				
			off_x = x_point_array[1] - skin_points[count][1]
			off_y = x_point_array[2] - skin_points[count][2]
			off_z = x_point_array[3] - skin_points[count][3]
			x_point_array = #(off_x, off_y, off_z)

			in coordsys skin_obj polyOp.setVert intermediate_object vert [y_array[1], y_array[2], y_array[3]]
			y_point_array = in coordsys skin_obj polyOp.getVert skin_obj vert

			off_x = y_point_array[1] - skin_points[count][1]
			off_y = y_point_array[2] - skin_points[count][2]
			off_z = y_point_array[3] - skin_points[count][3]
			y_point_array = #(off_x, off_y, off_z)

			in coordsys skin_obj polyOp.setVert intermediate_object vert [z_array[1], z_array[2], z_array[3]]
			z_point_array = in coordsys skin_obj polyOp.getVert skin_obj vert

			off_x = z_point_array[1] - skin_points[count][1]
			off_y = z_point_array[2] - skin_points[count][2]
			off_z = z_point_array[3] - skin_points[count][3]
			z_point_array = #(off_x, off_y, off_z)

			in coordsys skin_obj polyOp.setVert intermediate_object vert [intermediate_points[count][1], intermediate_points[count][2], intermediate_points[count][3]]

			extract_row_1 = [z_point_array[1],z_point_array[2],z_point_array[3]]
			extract_row_2 = [x_point_array[1],x_point_array[2],x_point_array[3]]
			extract_row_3 = [y_point_array[1],y_point_array[2],y_point_array[3]]
			extract_row_4 = [skin_points[count][1],skin_points[count][2],skin_points[count][3]]

			extract_matrix = (matrix3 extract_row_1 extract_row_2 extract_row_3 extract_row_4)

			result_matrix = (matrix3 [0,0,1] [1,0,0] [0,1,0] result_points[count])
			pt = target_points[count] * inverse extract_matrix
			pt *= result_matrix
			
			in coordsys result_obj polyOp.setVert result_obj vert [pt[1], pt[2], pt[3]]
		)
	)
)

extract = ExtractMorph()

struct AddMorpher
(
	morpherObj = undefined,
	target_obj = undefined,
	mod_index = undefined,
	chnl_index = undefined,

	fn find_morph_mod =
	(
		mod_index = undefined
		for i=1 to morpherObj.modifiers.count do
		(
			if (classOf morpherObj.modifiers[i]) == Morpher then
			(
				morpher_mod = morpherObj.modifiers[i]
				mod_index = i
			)
		)
	),
	
	fn get_indexes_target =
	(
		chnl_index = undefined
		chnl = 1
		morpher_mod = morpherObj.modifiers[mod_index]
		chnls_count = WM3_NumberOfChannels morpher_mod
		while chnl <= chnls_count and chnl_index == undefined do
		(
			chnl_state = WM3_MC_HasData morpher_mod chnl
			if chnl_state == false then
			(
				chnl_index = chnl
			)
			chnl += 1
		)
	),
	
	fn add_morpher_target =
	(
		morpher_mod = morpherObj.modifiers[mod_index]
		WM3_MC_BuildFromNode morpher_mod chnl_index target_obj
		WM3_MC_SetValue morpher_mod chnl_index 100.0
	)
)

add_morpher = AddMorpher()

fn morph_target =
(
	add_morpher.find_morph_mod()
	if add_morpher.mod_index != undefined then
	(
		add_morpher.get_indexes_target()
		add_morpher.add_morpher_target()
	)else
	(
		messageBox "You don't have morpher modifier."
	)
)

fn run_struct skin_obj target_obj =
(
	extract.complete = false
	extract.skin_obj = skin_obj
	extract.target_obj = target_obj
	extract.create_obj()
	extract.find_skin_mod()
	if extract.index != undefined then
	(
		extract.delete_mod extract.intermediate_object
		extract.delete_mod extract.result_obj all:true
		extract.skin_obj = extract.intermediate_object
		extract.intermediate_object = extract.skin_obj.baseobject
		
		extract.get_vertcount()
		
		if extract.vertcount != undefined then
		(
			extract.get_vertices_moved()
			extract.get_pos_vert()
			extract.find_offsets()
			convertToPoly extract.result_obj
			delete extract.skin_obj
			extract.complete = true
		)else
		(
			delete #(extract.skin_obj, extract.result_obj)
			messageBox ("Please, pick objs with same number of vertices.")
		)
	)else
	(
		delete #(extract.intermediate_object, extract.result_obj)
		messageBox ("No skin find on: " + extract.skin_obj.name)
	)
)

fn valid_geometry skin_obj target_obj =
(
	if classOf skin_obj.baseobject == Editable_Poly and classOf target_obj.baseobject == Editable_Poly then
	(
		run_struct skin_obj target_obj
	)else
	(
		messageBox "Your geometries aren't an Editable Poly."
	)
)

rollout extract_morph_ro "Extract Morph"
(
	pickButton skin_pckbtn "Pick Skin Obj" width:(extract_morph_ro.width-5) align:#center
	pickButton deform_pckbtn "Pick Deform Obj" width:(extract_morph_ro.width-5) align:#center
	checkbox morph_chk "Add to morpher modifier" checked:false align:#left
	group "Name morpher"
	(
		editText name_edt "" across:2 enabled:false align:#center
		checkbox name_chk "Default" checked:true align:#center
	)
	button create_btn "Create" align:#center

	on skin_pckbtn picked obj do
	(
		skin_pckbtn.text = obj.name
	)
	
	on skin_pckbtn rightclick do
	(
		skin_pckbtn.text = "Pick Skin Obj"
	)
	
	on deform_pckbtn picked obj do
	(
		deform_pckbtn.text = obj.name
	)
	
	on deform_pckbtn rightclick do
	(
		deform_pckbtn.text = "Pick Deform Obj"
	)
	
	on name_chk changed state do
	(
		name_edt.enabled = not name_chk.checked
	)
	
	on create_btn pressed do
	(
		complete = false
		if name_edt.enabled == true then
		(
			extract.result_name = name_edt.text
		)
		if skin_pckbtn.text != "Pick Skin Obj" and deform_pckbtn.text != "Pick Deform Obj" then
		(
			skin_obj = getNodeByName skin_pckbtn.text
			target_obj = getNodeByName deform_pckbtn.text

			if classOf skin_obj.baseobject == Editable_Poly and classOf target_obj.baseobject == Editable_Poly then
			(
				run_struct skin_obj target_obj
			)else
			(
				messageBox "Your geometries aren't an Editable Poly."
			)
		)
		
		if extract.complete == true and morph_chk.checked == true then
		(
			add_morpher.morpherObj = skin_obj
			add_morpher.target_obj = extract.result_obj
			morph_target()
		)
		update skin_obj
		skin_obj
	)
)

CreateDialog extract_morph_ro