*** Settings ***
Suite Setup       Suite Setup    ${n1_name}    ${n1_ip}
Suite Teardown    # Suite Teardown    ${n1_name}
Library           F7Library    ned

*** Variables ***
${n1_name}        my_node
${n1_ip}          10.16.24.16
${r1_sh}          2
${r1_slot}        8
${r2_sh}          11
${r2_slot}        1
${ch1}            19590

*** Test Cases ***
Create Mod
    ${r1_mod}    Set Variable    MOD-${r1_sh}-${r1_slot}
    ${r2_mod}    Set Variable    MOD-${r2_sh}-${r2_slot}
    Create Entity    ${r1_mod}    ROADMNO=1    TYPE__EQUIPMENT=4ROADM-C96    ADMIN=IS    MODE=N-FIXED    CHA__SPC=FLEX
    ...    CHANNELS=96    ALIAS=min

Create Om
    ${r1_om_n}    Set Variable    OM-${r1_sh}-${r1_slot}-N
    ${r1_om_c1}    Set Variable    OM-${r1_sh}-${r1_slot}-C1
    ${r2_om_n}    Set Variable    OM-${r2_sh}-${r2_slot}-N
    ${r2_om_c2}    Set Variable    OM-${r2_sh}-${r2_slot}-C2
    #    Create Entity    ${r1_om_n}    ADMIN=IS    OPTSET=-19    TILT=-1    OFFSET=2
    #    Create Entity    ${r1_om_c1}    ADMIN=IS
    #    Create Entity    ${r1_om_n}
    Create Entity    ${r2_om_c2}

Create Crs-EOU
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    ${crs_add}    Set Variable    CRS_CH-${r1_vch_c1_ch1},${r1_vch_n_ch1}
    ${crs_drop}    Set Variable    CRS_CH-${r1_vch_n_ch1},${r1_vch_c1_ch1}
    Create Entity    ${crs_add}    PATH-NODE=1    EOU=${True}
    #    Create Entity    ${crs_drop}    PATH-NODE=1    CONFIG__CRS=DROP    TYPE__FACILITY=OPTICAL    EOU=${True}

Create Vch
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    Create Entity    ${r1_vch_n_ch1}    ADMIN=IS    CHAN-BW=50G    EQLZ-ADMIN=ENABLE
    Create Entity    ${r1_vch_c1_ch1}    ADMIN=IS    CHAN-BW=50G

Create Crs
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    ${crs_add}    Set Variable    CRS_CH-${r1_vch_c1_ch1},${r1_vch_n_ch1}
    ${crs_drop}    Set Variable    CRS_CH-${r1_vch_n_ch1},${r1_vch_c1_ch1}
    #    Create Entity    ${crs_add}    PATH-NODE=1    EOU=${True}
    Create Entity    ${crs_drop}    PATH-NODE=1    CONFIG__CRS=DROP    TYPE__FACILITY=OPTICAL

Delete Crs
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    ${crs_add}    Set Variable    CRS_CH-${r1_vch_c1_ch1},${r1_vch_n_ch1}
    ${crs_drop}    Set Variable    CRS_CH-${r1_vch_n_ch1},${r1_vch_c1_ch1}
    Destroy Entity    ${crs_add}
    Destroy Entity    ${crs_drop}

Set
    Set Entity Param    ${aid}    ADMIN    MT
    Set Entity Param    ${aid}    ADMIN=IS

Get
    #    ${admin}    Get Entity Param    MOD-2-6    ADMIN
    #    ${admin}    Get Entity Param    MOD-2-7    ADMIN
    #    ${admin}    Get Entity Param    MOD-2-8    ADMIN
    #    ${type}    Get Entity Param    ${aid}    EP_TYPE__EQUIPMENT
    #    ${type}    Get Entity Param    MOD-2-6    TYPE__EQUIPMENT
    #    ${type}    Get Entity Param    MOD-2-7    TYPE__EQUIPMENT
    ${type}    Get Entity Param    MOD-2-8    TYPE__EQUIPMENT

Destroy
    Destroy Entity    ${aid}

Force Delete
    Force Destroy Entity    MOD-11-4

*** Keywords ***
Suite Setup
    [Arguments]    ${name}    ${ip}
    Open Named Connection    ${name}    ${ip}

Suite Teardown
    [Arguments]    ${name}
    Close Connection    ${name}
