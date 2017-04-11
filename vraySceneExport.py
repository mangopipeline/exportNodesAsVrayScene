'''
Vray Scene Object Export
By Carlos Anguiano
Mangosoft LLC
carlos@mangopipleine.com
http://mangopipleine.com 
convinance method for exporting objects in maya to a vray scene regardless of visiblity
'''
from maya import cmds,mel
import os

def attrListToDic(attrList):
    #combinaince methods for quickly storing attribute values
    out = {}
    for a in attrList:
        out[a] = cmds.getAttr(a)
    return out
    
def setAttrsFromDic(dic):
    #combinance method for restoring attribute values from a given dictionary
    for k,val in dic.iteritems():
        if val == None:
            cmds.setAttr(k,'',type='string')
            continue
        if type(val) in (str,unicode):
            val = str(val)
            cmds.setAttr(k,val,type='string')
            continue
        cmds.setAttr(k,val)
    
def exportNodesToVrayScene(nodeList,fpn,range=None):
    '''
    THE BIG CHEESE
    this is th main method here's the inputs
    nodeList list of nodes you would like to export 
    fpn the name of your output file example c:\temp\objects.vrscene
    range optional tuple with the first and last frame if you need to export of a time range the default of none sets it to export only the current frame
    '''
    if not len(nodeList):
        print 'ERROR: select some nodes homie'
        return False
    
    #this snippet is used to set the visiblity of objects back to on in the vrscene...
    code = str('''
from vray.utils import *
nodes=findByType("Node")
for i in nodes:i.set("visible", 1)
''')
    
    #make sure we set vray as the active render...
    plugins = {'vrayformaya.mll':False,
               'xgenVRay.py':False}

    #if vray is not the current render then lets try to make it so...
    if mel.eval('currentRenderer()') != 'vray':
        #check if vray dlls are loaded and if they are not load them
        for p in plugins:
            if cmds.pluginInfo(p,q=True,l=True):
                plugins[p] = True
                continue
            val = cmds.loadPlugin( p,quiet=True)
            if not val:continue
            plugins[p] = True
        
        #if we fail to at least load vrayformaya.mll let's quit out :(    
        if not plugins['vrayformaya.mll']:
            print 'method exportNodesToVrayScene could not load vray, sorry booboo'
            return False
        
        #now that vray is loaded let's set it as the current renderer
        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'vray', type='string' )
    
    #now that vray has been set let's add a vray settings node if it doesn't exist
    if not cmds.objExists('vraySettings'):mel.eval('vrayCreateVRaySettingsNode()')
    
    #capture settings
    attrs = ['vraySettings.globopt_geom_doHidden',
             'vraySettings.postTranslatePython',
             'vraySettings.vrscene_render_on',
             'vraySettings.vrscene_on',
             'vraySettings.vrscene_filename',
             'vraySettings.animType',
             'defaultRenderGlobals.startFrame',
             'defaultRenderGlobals.endFrame',
             'defaultRenderGlobals.byFrameStep']
    
    
    backUp =    attrListToDic(attrs) 
    
    #let's now apply all our export settings
    cmds.setAttr('vraySettings.globopt_geom_doHidden',2)
    cmds.setAttr('vraySettings.postTranslatePython',code,type='string')
    cmds.setAttr("vraySettings.vrscene_render_on",False)
    cmds.setAttr("vraySettings.vrscene_on", True)
    cmds.setAttr('vraySettings.vrscene_filename',fpn,type='string')
    cmds.setAttr("vraySettings.animType",0)
    
    #if a range is provided (tuple first and last frame)
    if range:
        cmds.setAttr('vraySettings.animType',1)
        cmds.setAttr('defaultRenderGlobals.startFrame',range[0])
        cmds.setAttr('defaultRenderGlobals.endFrame',range[1])
        cmds.setAttr('defaultRenderGlobals.byFrameStep',1.0)
    
    #export
    if os.path.isfile(fpn):os.remove(fpn)
    
    ndLString = ' '.join(nodeList)
    print '--->NodeString=',ndLString
    cmds.vrend(bat=True,exportSpecific=ndLString)
            
    #restore settings
    setAttrsFromDic(backUp)
    
    #check to see that our file was written out
    if not os.path.isfile(fpn):
        print 'looks like the export failed output path could not be verified'
        return False

    
    return True
            
   
    
if __name__ == '__main__':
    objs = cmds.ls(sl=True)
    exportNodesToVrayScene(objs,r'c:\temp\testVrayScene.vrscene')