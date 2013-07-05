import re
import hou

def literalsToParms(nodes):
	for node in nodes:
		snippet_parm = node.parm('snippet')
		snippet = snippet_parm.eval()

		vex_lines = snippet.strip().split("\n")

		declarations = _findDeclarations(vex_lines)
		parm_type = None
		

		tempGroup = node.parmTemplateGroup()

		sep = tempGroup.find('auto_generated')
		
		if not sep:
		    sep = hou.SeparatorParmTemplate('auto_generated')

		    tempGroup.insertBefore(tempGroup.entries()[0], sep)

		for decl in declarations:
		    linenum, vartype, varname, varvalue = decl
		    
		    template = None
		    numComps = None

		    if vartype == 'float':
		        template = hou.FloatParmTemplate(varname, varname, 1)
		        parm_type = template.type()
		        numComps = 1
		    if vartype == 'int':
		        template = hou.IntParmTemplate(varname, varname, 1)
		        parm_type = template.type()
		        numComps = 1
		    elif vartype == 'vector':
		        template = hou.FloatParmTemplate(varname, varname, 3)
		        parm_type = template.type()
		        numComps = 3
		    elif vartype == 'vector4':
		        template = hou.FloatParmTemplate(varname, varname, 4)
		        parm_type = template.type()
		        numComps = 4

		    if parm_type == hou.parmTemplateType.Float:
		        valtype = float
		    else:
		        valtype = int

		    g = re.match(r"[\{\s]*([0-9\.\ f\,]*).*", varvalue).groups()[0]
		    varvalue  = [valtype(comp) for comp in g.split(',')]

		    
		    if template:
		        existing_template = tempGroup.find(varname)
		        
		        if not existing_template:
		            pass
		        elif existing_template.type() != parm_type:
		            existing_template = None
		            tempGroup.remove(varname)
		        elif existing_template.numComponents() != numComps:
		            existing_template = None
		            tempGroup.remove(varname)
		        else:
		            template = existing_template

		        template.setNumComponents(numComps)

		        template.setDefaultValue(varvalue)

		        if not existing_template:
		            tempGroup.insertBefore(sep, template)
		        if template == existing_template:
		            tempGroup.replace(varname, template)
		        
		        vex_lines[linenum] = "%s %s = ch(\"%s\");" % (vartype, varname, varname)
		        
		        
		node.setParmTemplateGroup(tempGroup)
		new_code = "\n".join(vex_lines)
		snippet_parm.set(new_code)

def _findDeclarations(vex_code_lines):
    decl = []
    
    # find simple assignments
    for i, line in enumerate(vex_code_lines):
        # match word word = number or {number, number, ...}
        m = re.match(r"([@\w]+) ([@\w]+) *\= *({.*}|[0-9\.]*)", line)
        
        if not m: continue
        
        vartype, varname, value = m.groups()
        
        if not value: continue
        
        decl.append((i, vartype, varname, value))
    
    return decl


