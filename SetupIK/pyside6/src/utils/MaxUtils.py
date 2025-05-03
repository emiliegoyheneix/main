from pymxs import runtime as rt # type: ignore

class MaxUtilsIKChain:
    def __init__(self, prefix=""):
        self.objs_hi_names = [  f"{prefix}root_PT",
                                f"{prefix}start_PT",
                                f"{prefix}end_PT",
                                f"{prefix}softblend_PT",
                                f"{prefix}ctrl_PT"]

    def setup_ik_chain(self):
        sel = rt.getCurrentSelection()
        for obj in sel:
            hdl = self.check_sel(obj)
            if hdl:
                hdl.controller.posThresh = 0.0001
                hdl_jnts = self.get_jnts_hdl(hdl)
                objs_hi = self.build_hierarchy(hdl, hdl_jnts)
                Attribute_Holder = self.add_attr(objs_hi, hdl_jnts)
                self.constr(objs_hi, Attribute_Holder)
                self.add_scale_controller(objs_hi, hdl_jnts)
                self.set_exp(hdl_jnts, objs_hi)
                #self.add_layer(hdl, objs_hi)

    def add_layer(self, hdl, objs_hi):
        layer = hdl.layer
        for obj in objs_hi:
            layer.addnode(obj)

    def check_sel(self, obj):
        hdl = None
        node_type = rt.classOf(obj)
        if node_type == rt.IK_Chain_Object:
            hdl = obj
            return hdl
        return None

    def get_jnts_hdl(self, hdl):
        start = hdl[2].controller.startJoint
        end = hdl[2].controller.endJoint
        node_child = start
        hdl_jnts = []
        while node_child != end:
            hdl_jnts.append(node_child)
            node_child = node_child.children[0]
        hdl_jnts.append(node_child)
        return hdl_jnts

    def build_hierarchy(self, hdl, hdl_jnts):
        objs_hi = self.create_hi(hdl_jnts, hdl)
        self.lookat(objs_hi)
        return objs_hi

    def freeze_transform(self, item):
        try:
            rt.setPropertyController(item.controller, 'Rotation', rt.Euler_XYZ())
            rt.setPropertyController(item.controller, 'Rotation', rt.RotationList())
            roControl = rt.getPropertyController(item.controller, 'Rotation')
            rt.SetPropertyController(roControl, "Available", rt.Euler_XYZ())
            roControl.setName(1, "Frozen Rotation")
            roControl.setName(2, "Zero Euler XYZ")
            roControl.SetActive(2)
        except:
            pass
            
        try:
            item = rt.getCurrentSelection()[0]
            rt.setPropertyController(item.controller, 'Position', rt.Bezier_Position())
            rt.setPropertyController(item.controller, 'Position', rt.position_list())
            roControl = rt.getPropertyController(item.controller, 'Position')
            rt.SetPropertyController(roControl, "Available", rt.Position_XYZ())
            roControl.setName(1, "Frozen Position")
            roControl.setName(2, "Zero Pos XYZ")
            roControl.SetActive(2)		
        except:
            pass

    def create_hi(self, hdl_jnts, hdl, objs_hi=[1,2,3,4,5]):
        objs_hi[0] = rt.Point(transform=hdl_jnts[0].transform, name=rt.uniqueName(self.objs_hi_names[0]))
        objs_hi[1] = rt.Point(transform=hdl_jnts[0].transform, name=rt.uniqueName(self.objs_hi_names[1]))
        objs_hi[2] = rt.Point(transform=hdl_jnts[-1].transform, name=rt.uniqueName(self.objs_hi_names[2]))
        objs_hi[3] = rt.Point(transform=hdl_jnts[-1].transform, name=rt.uniqueName(self.objs_hi_names[3]))
        objs_hi[4] = rt.Point(transform=hdl_jnts[-1].transform, name=rt.uniqueName(self.objs_hi_names[4]))
        
        hdl_jnts[0].parent = objs_hi[1]
        objs_hi[2].parent = objs_hi[1]            
        objs_hi[1].parent = objs_hi[0]
        objs_hi[3].parent = objs_hi[0]
        objs_hi[4].parent = objs_hi[0]
        hdl.parent = objs_hi[3]
                
        #freeze_transform(objs_hi[4])
        return objs_hi
    
    def lookat(self, objs_hi):
        Look_At = rt.LookAt_Constraint()
        rt.setPropertyController(objs_hi[1].controller, 'Rotation', Look_At)
        Look_At.appendTarget(objs_hi[4], 50)
        Look_At.upnode_world = False
        Look_At.pickUpNode = objs_hi[0]
        objs_hi[2].transform = objs_hi[4].transform
        
    def add_attr(self, objs_hi, hdl_jnts):
        Attribute_Holder = rt.emptyModifier()
        rt.addModifier(objs_hi[4], Attribute_Holder)
        Lenghts_params = ""
        Lenghts_rollout = ""
        bones = 1
        for count, jnt in enumerate(hdl_jnts[:-1]):
            lab = f'label Length_{count+1}_lab "Length_{count+1}:" Align:#Left\n'
            spn = f'spinner Length_{count+1}_spn "" range:[0,10,1] offset:[0,-20] Align:#Right\n'
            param = f'Length_{count+1}_param type:#float ui:Length_{count+1}_spn\n'
            Lenghts_rollout += (lab + spn)
            Lenghts_params += param
            bones += count

        ca=f"""attributes "ik_ctrl"
        (
            parameters main rollout:params
            (
                stretch_param type:#float ui:stretch_spn
                soft_param type:#float ui:soft_spn
                squash_param type:#float ui:squash_spn
                volume_param type:#float ui:volume_spn
                {Lenghts_params}
            )
            rollout params "IK Controls"
            (
                label stretch_lab "Stretch:" Align:#Left
                spinner stretch_spn "" range:[0,1,0] offset:[0,-20] Align:#Right
                label soft_lab "SoftIK:" Align:#Left
                spinner soft_spn "" range:[0,10,0] offset:[0,-20] Align:#Right
                label squash_lab "Squash:" Align:#Left
                spinner squash_spn "" range:[0,1,0] offset:[0,-20] Align:#Right
                label volume_lab "Volume:" Align:#Left
                spinner volume_spn "" range:[0,1,0] offset:[0,-20] Align:#Right
                {Lenghts_rollout}
            )
        )"""
        attr = rt.execute(ca)
        rt.custAttributes.add(Attribute_Holder, attr)
        for count in range(bones):
            try:
                print(objs_hi[4].modifiers[0].ik_ctrl[count+4])
                objs_hi[4].modifiers[0].ik_ctrl[count+4].value = 1.0
            except:
                pass
        return Attribute_Holder
        
    def constr(self, objs_hi, Attribute_Holder):
        position_constraint = rt.Position_Constraint()
        rt.setPropertyController(objs_hi[3].controller, 'Position', position_constraint)
        position_constraint.appendTarget(objs_hi[2], 100)
        position_constraint.appendTarget(objs_hi[4], 100)
        rt.paramWire.connect(Attribute_Holder.ik_ctrl[0], position_constraint[0], "1 - stretch_param")
        rt.paramWire.connect(Attribute_Holder.ik_ctrl[0], position_constraint[1], "stretch_param")
        
    def add_scale_controller(self, objs_hi, hdl_jnts):
        scale_xyz = rt.ScaleXYZ()
        rt.setPropertyController(objs_hi[0].controller, 'Scale', scale_xyz)
        
    def set_exp(self, hdl_jnts, objs_hi):
        self.set_volume(hdl_jnts, objs_hi)
        self.set_soft_exp(hdl_jnts, objs_hi)
        self.set_stretch_squash_exp(hdl_jnts, objs_hi)
        
    def set_soft_exp(self, hdl_jnts, objs_hi):
        float_script = rt.float_script()
        pos_ctrl = rt.getPropertyController(objs_hi[2].controller, 'Position')
        rt.setPropertyController(pos_ctrl, 'X Position', float_script)
        
        chainlen = ""
        for count, jnt in enumerate(hdl_jnts[:-1]):
            length = str(jnt.length)
            float_script.AddTarget(f"Length_{count+1}_param", objs_hi[4].modifiers[0].ik_ctrl[rt.name(f"Length_{count+1}_param")])
            chainlen += f"{length} * Length_{count+1}_param + "
        chainlen = chainlen[:-2]
        self.chainlen = chainlen
        
        float_script.AddConstant("ctrl", objs_hi[4])
        rot_ctl = rt.getPropertyController(objs_hi[0].controller, 'Scale')
        rot_x_ctrl = rt.getPropertyController(rot_ctl, 'X Scale')
        float_script.AddTarget("rootscale", rot_x_ctrl)
        float_script.AddTarget("soft_param", objs_hi[4].modifiers[0].ik_ctrl[rt.name("soft_param")])#Attribute_Holder
        float_script.AddConstant("start_bone_pt", objs_hi[1])
        script = f"""   controlDist = distance start_bone_pt ctrl * 100 / rootscale
                        chainlen = {chainlen}
                        softPos = controlDist\n
                        if controlDist > (chainlen - soft_param) then
                        (
                            softPos = chainlen - soft_param * exp(-(controlDist - (chainlen - soft_param)) / soft_param)
                        )
                        softPos
                        """
        script = "\n".join([line.strip() for line in script.splitlines() if line.strip()])
        float_script.script = script
        
    def set_stretch_squash_exp(self, hdl_jnts, objs_hi):
        chainlen = self.chainlen
        for count, jnt in enumerate(hdl_jnts[:-1]):
            float_script = rt.float_script()
            pos_ctrl = rt.getPropertyController(hdl_jnts[count+1].controller[3], 'Position')
            rt.setPropertyController(pos_ctrl, 'X Position', float_script)
            
            for i, j in enumerate(hdl_jnts[:-1]):
                float_script.AddTarget(f"Length_{i+1}_param", objs_hi[4].modifiers[0].ik_ctrl[rt.name(f"Length_{i+1}_param")])
        
            float_script.AddConstant("ctrl", objs_hi[4])
            scale_ctl = rt.getPropertyController(objs_hi[0].controller, 'Scale')
            scale_x_ctrl = rt.getPropertyController(scale_ctl, 'X Scale')
            float_script.AddTarget("rootscale", scale_x_ctrl)
            float_script.AddConstant("softblendp", objs_hi[3])
            float_script.AddTarget("soft_param", objs_hi[4].modifiers[0].ik_ctrl[rt.name("soft_param")])#Attribute_Holder
            float_script.AddTarget("squash_param", objs_hi[4].modifiers[0].ik_ctrl[rt.name("squash_param")])#Attribute_Holder
            float_script.AddTarget("stretch_param", objs_hi[4].modifiers[0].ik_ctrl[rt.name("stretch_param")])#Attribute_Holder
            float_script.AddConstant("start_bone_pt", objs_hi[1])
            float_script.AddConstant("end_bonept", objs_hi[2])
            float_script.AddConstant("bonelen", float(jnt.length))
            float_script.AddConstant("dist", rt.distance(objs_hi[1], objs_hi[4]))
            float_script.AddConstant("bones", (len(hdl_jnts)-1))
            script = f"""   softlen = distance softblendp end_bonept * 100 / rootscale
                            bonelen = bonelen * Length_{count+1}_param
                            chainlen = {chainlen}
                            stretchlen = chainlen
                            controlDist = distance start_bone_pt ctrl * 100 / rootscale
                            softPos = controlDist
                            val = (softLen * (boneLen / chainLen) * stretch_param + boneLen)
                            if squash_param > 0 then
                            (
                                if (controlDist - softLen) < dist then
                                (
                                    val = boneLen - ((dist - controlDist) / bones) * squash_param
                                )
                            )
                            val
                            """
            #if (controlDist) < dist then
            #(
            #    val = boneLen - ((dist - controlDist) / bones) * squash_param + (softlen / bones)
            #)
            script = "\n".join([line.strip() for line in script.splitlines() if line.strip()])
            float_script.script = script
            
    def set_volume(self, hdl_jnts, objs_hi):
        for count, jnt in enumerate(hdl_jnts[:-1]):
            copy_jnt = rt.copy(jnt)
            copy_jnt.transform = jnt.transform
            copy_jnt.name = (jnt.name + "_scale")
            copy_jnt.parent = jnt
            
            scale_xyz = rt.ScaleXYZ()
            rt.setPropertyController(copy_jnt.controller[3], 'Scale', scale_xyz)
            self.scale_x(scale_xyz, objs_hi, count, hdl_jnts, jnt)
            
            for axis in ["Y", "Z"]:
                float_script = rt.float_script()
                rt.setPropertyController(scale_xyz, f'{axis} Scale', float_script)
                float_script.AddTarget(f"Length_{count+1}_param", objs_hi[4].modifiers[0].ik_ctrl[rt.name(f"Length_{count+1}_param")])
                float_script.AddTarget("volume_param", objs_hi[4].modifiers[0].ik_ctrl[rt.name("volume_param")])#Attribute_Holder
                float_script.AddConstant("bonelen", float(jnt.length))
                pos_ctrl = rt.getPropertyController(hdl_jnts[count+1].controller[3], 'Position')
                pos_x_ctrl = rt.getPropertyController(pos_ctrl, 'X Position')
                float_script.AddTarget("jnt_translateX", pos_x_ctrl)
                script = f"""   val = 1.0
                                bonelen = bonelen * Length_{count+1}_param
                                if volume_param > 0 then
                                (
                                    if Length_{count+1}_param > 0 then
                                    (
                                        val = 1 + ((boneLen / jnt_translateX) - 1) * volume_param
                                    )
                                )
                                val
                                """
                script = "\n".join([line.strip() for line in script.splitlines() if line.strip()])
                float_script.script = script
            rt.hide(jnt)
            
    def scale_x(self, scale_xyz, objs_hi, count, hdl_jnts, jnt):
        float_script = rt.float_script()
        rt.setPropertyController(scale_xyz, 'X Scale', float_script)
        scale_ctl = rt.getPropertyController(objs_hi[0].controller, 'Scale')
        scale_x_ctrl = rt.getPropertyController(scale_ctl, 'X Scale')
        float_script.AddTarget("rootscale", scale_x_ctrl)
        float_script.AddConstant("bonelen", float(jnt.length))
        float_script.AddConstant("p0", hdl_jnts[count])
        float_script.AddConstant("p1", hdl_jnts[count+1])
        script = f"""((distance p0 p1)/bonelen) * 100 / rootscale"""
        script = "\n".join([line.strip() for line in script.splitlines() if line.strip()])
        float_script.script = script