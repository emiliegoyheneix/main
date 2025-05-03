import maya.cmds as cmds

class MayaUtilsIKHandle:
    def __init__(self, prefix=""):
        self.root_orient = ""
        self.rootscale = ""
        self.controlDist = ""
        self.softP = ""
        self.squashP = ""
        self.stretchP = ""
        self.softLen = ""
        self.dist = ""
        self.bones = ""
        self.volumeP = ""
        self.lengths_expr = ""
        self.chainlen_expr = ""
        self.lengths = []
        self.boneLen = []
        self.chainlen = []
        self.objs_hi_names = [  f"{prefix}_root_LOC",
                                f"{prefix}_start_LOC",
                                f"{prefix}_end_LOC",
                                f"{prefix}_softblend_LOC",
                                f"{prefix}_ctrl_LOC"]
        
        self.dists_names = [f"{prefix}_group_dist",
                            f"{prefix}_control_dist",
                            f"{prefix}_soft_dist",
                            f"{prefix}_stretch_dist"]
        
    def setup_ik_handle(self):
        sel = cmds.ls(selection=True)
        for obj in sel:
            hdl = self.check_sel(obj)
            if hdl:
                hdl_jnts = self.get_jnts_hdl(hdl)
                objs_hi, dists = self.build_hierarchy(hdl, hdl_jnts)
                self.add_attr(objs_hi[4], hdl_jnts)
                self.constr(objs_hi, objs_hi[4])
                self.get_variables(hdl_jnts, objs_hi, dists)
                self.set_exp(hdl_jnts, objs_hi, dists)
        
    def check_sel(self, obj):
        hdl = None
        node_type = cmds.nodeType(obj)
        if node_type == "ikHandle":
            hdl = obj
            return hdl
        return None

    def get_jnts_hdl(self, hdl):
        hdl_jnts = cmds.ikHandle(hdl, query=True, jointList=True)
        end_jnt = cmds.listRelatives(hdl_jnts[-1], children=True, type="joint")
        hdl_jnts += end_jnt
        return hdl_jnts
    
    def build_hierarchy(self, hdl, hdl_jnts):
        objs_hi = self.check_name(self.objs_hi_names)
        self.create_hi(objs_hi, hdl_jnts, hdl)#le ctrl_LOC sera parenté au ctrl du IK
        dists = self.check_name(self.dists_names) 
        dists = self.create_node_dist(objs_hi, dists)
        return objs_hi, dists
    
    def check_name(self, objs):
        for index, obj in enumerate(objs):
            count = 1
            while cmds.objExists(obj):
                obj = f"{objs[index]}_{count:02}"
                count += 1
            objs[index] = obj
        return objs

    def create_hi(self, objs_hi, hdl_jnts, hdl):
        for obj in objs_hi:
            cmds.spaceLocator(name=obj)[0]
        cmds.matchTransform(objs_hi[0], objs_hi[1], hdl_jnts[0])
        cmds.matchTransform(objs_hi[2], objs_hi[3], objs_hi[4], hdl_jnts[-1])
        cmds.parent(objs_hi[2], objs_hi[1])
        cmds.parent(hdl, objs_hi[3])
        cmds.parent(objs_hi[3], objs_hi[4], objs_hi[1], objs_hi[0])
        cmds.parent(hdl_jnts[0], objs_hi[1])
        cmds.aimConstraint(objs_hi[4], objs_hi[1], offset=(0, 0, 0), aimVector=(1, 0, 0), upVector=(0, 1, 0),
                            worldUpType="objectrotation", worldUpVector=(0, 1, 0), worldUpObject=objs_hi[0])
        cmds.matchTransform(objs_hi[2], hdl_jnts[-1])

    def create_node_dist(self, objs_hi, dists):
        group_dist = cmds.group(em=True, name=dists[0])
        control_dist = cmds.createNode('distanceDimShape', name=dists[1], parent=group_dist)
        cmds.connectAttr(f"{objs_hi[1]}.worldPosition[0]", f"{control_dist}.startPoint", force=True)
        cmds.connectAttr(f"{objs_hi[4]}.worldPosition[0]", f"{control_dist}.endPoint", force=True)
        soft_dist = cmds.createNode('distanceDimShape', name=dists[2], parent=group_dist)
        cmds.connectAttr(f"{objs_hi[2]}.worldPosition[0]", f"{soft_dist}.startPoint", force=True)
        cmds.connectAttr(f"{objs_hi[3]}.worldPosition[0]", f"{soft_dist}.endPoint", force=True)
        stretch_dist = cmds.createNode('distanceDimShape', name=dists[3], parent=group_dist)
        cmds.connectAttr(f"{objs_hi[1]}.worldPosition[0]", f"{stretch_dist}.startPoint", force=True)
        cmds.connectAttr(f"{objs_hi[3]}.worldPosition[0]", f"{stretch_dist}.endPoint", force=True)
        return ([group_dist] + cmds.listRelatives(group_dist))

    def add_attr(self, hdl, hdl_jnts):
        cmds.addAttr(hdl, longName="Stretch", attributeType="double", minValue=0, maxValue=1, defaultValue=0, keyable=True)
        cmds.addAttr(hdl, longName="Soft", attributeType="double", minValue=0, maxValue=10, defaultValue=0, keyable=True)
        cmds.addAttr(hdl, longName="Squash", attributeType="double", minValue=0, maxValue=1, defaultValue=0, keyable=True)
        cmds.addAttr(hdl, longName="Volume", attributeType="double", minValue=0, maxValue=1, defaultValue=0, keyable=True)
        for jnt in hdl_jnts[:-1]:
            cmds.addAttr(hdl, longName=f"Length_{jnt}", attributeType="double", minValue=0.001, defaultValue=1, keyable=True)

    def constr(self, objs_hi, ctrl):
        pc = cmds.pointConstraint(objs_hi[4], objs_hi[2], objs_hi[3])[0]#verifier que le nom est libre
        rev = cmds.createNode('reverse')#verifier que le nom est libre
        cmds.connectAttr(f"{ctrl}.Stretch", f"{rev}.inputX", force=True)
        cmds.connectAttr(f"{ctrl}.Stretch", f"{pc}.{objs_hi[4]}W0", force=True)
        cmds.connectAttr(f"{rev}.outputX", f"{pc}.{objs_hi[2]}W1", force=True)

    def set_exp(self, hdl_jnts, objs_hi, dists):
        self.set_soft_exp(objs_hi)
        self.set_strech_squash_exp(objs_hi, hdl_jnts, dists)
        self.set_volume_exp(hdl_jnts, objs_hi, dists)
 
    def get_variables(self, hdl_jnts, objs_hi, dists):
        self.get_root_var(hdl_jnts, objs_hi, dists)

    def get_root_var(self, hdl_jnts, objs_hi, dists):
        # Récupère l'orientation du premier joint (X, Y, Z)
        self.root_orient = cmds.getAttr(f"{hdl_jnts[0]}.jot")[0].upper()
        # Création des chaînes de caractères dynamiques pour l'expression
        self.rootscale = f"{objs_hi[0]}.scale{self.root_orient}"
        self.controlDist = f"{dists[1]}.distance"
        self.softP = f"{objs_hi[4]}.Soft"
        self.squashP = f"{objs_hi[4]}.Squash"
        self.stretchP = f"{objs_hi[4]}.Stretch"
        self.softLen = f"{dists[2]}.distance"
        self.dist = f"{cmds.getAttr(f'{dists[1]}.distance')}"
        self.bones = f"{len(hdl_jnts) - 1}"
        self.volumeP = f"{objs_hi[4]}.Volume"

        # Initialisation des listes pour les longueurs et la chaîne
        self.lengths = []
        self.lengths_attr = []
        self.lengths_var = []
        self.boneLen = []
        self.chainlen = []
        # Boucle sur les joints pour générer les longueurs
        for count, jnt in enumerate(hdl_jnts[:-1]):
            self.lengths_var.append(f"$Length_{jnt}")
            self.lengths_attr.append(f"{objs_hi[4]}.Length_{jnt}")
            self.lengths.append(f"$Length_{jnt} = {objs_hi[4]}.Length_{jnt};\n")
            
            size_jnt = abs(cmds.getAttr(f'{hdl_jnts[count + 1]}.translate{self.root_orient}'))
            self.boneLen.append(f"$boneLen = ({size_jnt} * $Length_{jnt});\n")
            self.chainlen.append(f"({size_jnt} * $Length_{jnt})")
            

        # Fusionne les longueurs pour créer la chaîne totale
        self.chainlen_expr = f"{' + '.join(self.chainlen)}"
        self.lengths_expr = "".join(self.lengths)

 
    def set_soft_exp(self, objs_hi):
        # Crée l'expression finale avec f-string et conditionnel
        cond = f"""
        $rootScale = {self.rootscale};
        $controlDist = {self.controlDist} * 1 / $rootScale;
        $softDist = $controlDist;
        $softP = {self.softP};
        {self.lengths_expr}
        $chainLen = {self.chainlen_expr};
        if ($controlDist > ($chainLen - $softP))
        {{
            if ($softP > 0)
            {{
                $softDist = $chainLen - $softP * exp(-($controlDist - ($chainLen - $softP)) / $softP);
            }}
            else
            {{
                $softDist = $chainLen;
            }}
        }}
        {objs_hi[2]}.translateX = $softDist;
        """
        #cond = "\n".join([line.strip() for line in cond.splitlines() if line.strip()])
        # Crée l'expression dans Maya
        cmds.expression(name="SoftIK", s=cond)

    def set_strech_squash_exp(self, objs_hi, hdl_jnts, dists):
        # Boucle pour chaque joint et créer l'expression dynamique
        for count, jnt in enumerate(hdl_jnts[:-1]):
            target = f"{hdl_jnts[count+1]}.translate{self.root_orient}"
            boneLen_current = self.boneLen[count]  # Récupère la longueur d'os du joint courant
            
            if cmds.getAttr(target) >= 0:
                val = "$val"
            else:
                val = "-$val"
                
            # Crée l'expression finale avec f-string et conditionnel
            cond = f"""
            $rootScale = {self.rootscale};
            $controlDist = {self.controlDist} * 1 / $rootScale;
            $softP = {self.softP};
            $SquashP = {self.squashP};
            $StretchP = {self.stretchP};
            $softLen = {self.softLen} * 1 / $rootScale;
            {self.lengths_expr}
            {boneLen_current}
            $chainLen = {self.chainlen_expr};
            $dist = {self.dist};
            $bones = {self.bones};
            $val = ($softLen * ($boneLen / $chainLen) * $StretchP + $boneLen);
            if ($SquashP > 0)
            {{
                if (($controlDist - $softLen) < $dist)
                {{
                    $val = $boneLen - (($dist - $controlDist) / $bones) * $SquashP;
                }}
            }}
            {target} = {val};
            """
            # Supprime les tabulations et espaces superflus
            cond = "\n".join([line.strip() for line in cond.splitlines() if line.strip()])

            # Crée l'expression dans Maya
            cmds.expression(name=f"StretchIK_{count}", s=cond)

    def set_volume_exp(self, hdl_jnts, objs_hi, dists):
        # Boucle pour chaque joint et créer l'expression dynamique
        for count, jnt in enumerate(hdl_jnts[:-1]):
            boneLen_current = self.boneLen[count]  # Récupère la longueur d'os du joint courant
            target_orient = cmds.getAttr(f"{jnt}.jot")[0].upper()
            # Gestion des axes secondaires en fonction de l'axe principal
            if target_orient == "X":
                o1 = "Y"
                o2 = "Z"
            elif target_orient == "Y":
                o1 = "X"
                o2 = "Z"
            elif target_orient == "Z":
                o1 = "X"
                o2 = "Y"
            # Assignation des valeurs d'échelle pour les axes secondaires
            target_1 = f"{jnt}.scale{o1}"
            target_2 = f"{jnt}.scale{o2}"

            # Crée l'expression finale avec f-string et conditionnel
            cond = f"""
            $volumeP = {self.volumeP};
            {self.lengths_var[count]} = {self.lengths_attr[count]};
            {boneLen_current}
            $val = 1.0;
            if ($volumeP > 0)
            {{
                if ({self.lengths_var[count]} > 0)
                {{
                    $val = 1 + (($boneLen / {hdl_jnts[count+1]}.translate{target_orient}) - 1) * $volumeP;
                }}
            }}
            {target_1} = $val;
            {target_2} = $val;
            """
            
            # Supprime les tabulations et espaces superflus
            cond = "\n".join([line.strip() for line in cond.splitlines() if line.strip()])

            # Crée l'expression dans Maya
            cmds.expression(name=f"VolumeIK_{count}", s=cond)