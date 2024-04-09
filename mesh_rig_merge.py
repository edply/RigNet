import maya.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
import numpy as np
import pymel.core as pm
import os
import glob
import argparse


def loadInfo(info_name, geo_name):
    f_info = open(info_name,'r')
    joint_pos = {}
    joint_hier = {}
    joint_skin = []
    for line in f_info:
        word = line.split()
        if word[0] == 'joints':
            joint_pos[word[1]] = [float(word[2]),  float(word[3]), float(word[4])]
        if word[0] == 'root':
            root_pos = joint_pos[word[1]]
            root_name = word[1]
            cmds.joint(p=(root_pos[0], root_pos[1],root_pos[2]), name = root_name)
        if word[0] == 'hier':
            if word[1] not in joint_hier.keys():
                joint_hier[word[1]] = [word[2]]
            else:
                joint_hier[word[1]].append(word[2])
        if word[0] == 'skin':
            skin_item = word[1:]
            joint_skin.append(skin_item)
    f_info.close()
    
    this_level = [root_name]
    while this_level:
        next_level = []
        for p_node in this_level:
            if p_node in joint_hier.keys():
                for c_node in joint_hier[p_node]:
                    cmds.select(p_node, r=True)
                    child_pos = joint_pos[c_node]
                    cmds.joint(p=(child_pos[0], child_pos[1],child_pos[2]), name = c_node)
                    next_level.append(c_node)
        this_level = next_level         
    cmds.joint(root_name, e=True, oj='xyz', sao='yup', ch=True, zso=True)
    cmds.skinCluster( root_name, geo_name)
    #print len(joint_skin)
    for i in range(len(joint_skin)):
        vtx_name = geo_name + '.vtx['+joint_skin[i][0]+']'
        transValue = []
        for j in range(1,len(joint_skin[i]),2):
            transValue_item = (joint_skin[i][j], float(joint_skin[i][j+1]))
            transValue.append(transValue_item) 
        #print vtx_name, transValue
        cmds.skinPercent( 'skinCluster1', vtx_name, transformValue=transValue)
    cmds.skinPercent( 'skinCluster1', geo_name, pruneWeights=0.01, normalize=False )
    return root_name, joint_pos


def getGeometryGroups():
    geo_list = []
    geometries = cmds.ls(type='surfaceShape')
    for geo in geometries:
        if 'ShapeOrig' in geo:
            '''
            we can also use cmds.ls(geo, l=True)[0].split("|")[0]
            to get the upper level node name, but stick on this way for now
            '''
            geo_name = geo.replace('ShapeOrig', '')
            geo_list.append(geo_name)
    if not geo_list:
        geo_list = cmds.ls(type='surfaceShape')
    return geo_list
    
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_mesh_filepath', required=True, type=str) 
    parser.add_argument('--input_rig_filepath', required=True, type=str) 
    args = parser.parse_args()

    input_mesh_filepath = args.input_mesh_filepath
    input_rig_filepath = args.input_rig_filepath
    output_filepath = f"{os.path.splitext(input_mesh_filepath)[0]}.fbx"

     
    # import obj
    cmds.file(new=True,force=True)
    cmds.file(input_mesh_filepath, o=True)

    # import info
    geo_list = getGeometryGroups()
    root_name, _ = loadInfo(input_rig_filepath, geo_list[0])
    
    # export fbx
    pm.mel.FBXExport(f=output_filepath)
