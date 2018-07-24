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
Sh-Create+Delete
    Create Entity    SHELF-3    TYPE__EQUIPMENT=SH7HU    ADMIN=IS
    Set Entity Param    FCU-3    ADMIN=DSBLD
    Destroy Entity    FCU-3
    Set Entity Param    SHELF-3    ADMIN=DSBLD
    Destroy Entity    SHELF-3

Sh-Create
    Create Entity    SHELF-3    TYPE__EQUIPMENT=SH7HU    ADMIN=IS

Mod-Create+Delete
    ${r1_mod}    Set Variable    MOD-${r1_sh}-${r1_slot}
    ${r2_mod}    Set Variable    MOD-${r2_sh}-${r2_slot}
    Create Entity    ${r1_mod}    ROADMNO=1    TYPE__EQUIPMENT=4ROADM-C96    ADMIN=IS    MODE=N-FIXED    CHA__SPC=FLEX
    ...    CHANNELS=96    ALIAS=min
    #    Create Entity    MOD-11-9    TYPE__EQUIPMENT=4WCC10G

Mod-Create
    ${r1_mod}    Set Variable    MOD-${r1_sh}-${r1_slot}
    ${r2_mod}    Set Variable    MOD-${r2_sh}-${r2_slot}
    Create Entity    ${r1_mod}    ROADMNO=1    TYPE__EQUIPMENT=4ROADM-C96    ADMIN=IS    MODE=N-FIXED    CHA__SPC=FLEX
    ...    CHANNELS=96    ALIAS=min

Om-Create+Delete
    ${r1_om_n}    Set Variable    OM-${r1_sh}-${r1_slot}-N
    ${r1_om_c1}    Set Variable    OM-${r1_sh}-${r1_slot}-C1
    ${r2_om_n}    Set Variable    OM-${r2_sh}-${r2_slot}-N
    ${r2_om_c2}    Set Variable    OM-${r2_sh}-${r2_slot}-C2
    #    Create Entity    ${r1_om_n}    ADMIN=IS    OPTSET=-19    TILT=-1    OFFSET=2
    #    Create Entity    ${r1_om_c1}    ADMIN=IS
    #    Create Entity    ${r1_om_n}
    Create Entity    ${r2_om_c2}

Om-Create
    ${r1_om_n}    Set Variable    OM-${r1_sh}-${r1_slot}-N
    ${r1_om_c1}    Set Variable    OM-${r1_sh}-${r1_slot}-C1
    ${r2_om_n}    Set Variable    OM-${r2_sh}-${r2_slot}-N
    ${r2_om_c2}    Set Variable    OM-${r2_sh}-${r2_slot}-C2
    #    Create Entity    ${r1_om_n}    ADMIN=IS    OPTSET=-19    TILT=-1    OFFSET=2
    #    Create Entity    ${r1_om_c1}    ADMIN=IS
    #    Create Entity    ${r1_om_n}
    Create Entity    ${r2_om_c2}

Crs-Create-EOU
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    ${crs_add}    Set Variable    CRS_CH-${r1_vch_c1_ch1},${r1_vch_n_ch1}
    ${crs_drop}    Set Variable    CRS_CH-${r1_vch_n_ch1},${r1_vch_c1_ch1}
    @{crosstype_list}    Create List    ADD    DROP    STEERABLE_DROP
    @{crosstype_passed_list}    Create List    ADD_DROP    STEERABLE_ADDDROP
    @{crosstype_failed_list}    Create List    2WAY_PASS    1WAY_PASS
    Create Entity    ${crs_add}    PATH-NODE=6    EOU=${True}    ALIAS=my_crs    CROSS_TYPE=ADD    TYPE__FACILITY=OTU3
    ...    PATH-NODE__REVERSE=4
    #    Create Entity    ${crs_drop}    PATH-NODE=2    EOU=${True}    ALIAS=my_crs    CROSS_TYPE=DROP
    ...    # TYPE__FACILITY=OTU3    PATH-NODE__REVERSE=3
    #    :FOR    ${crosstype}    IN    @{crosstype_list}
    #    \    Create Entity    ${crs_add}    PATH-NODE=6    EOU=${True}    ALIAS=my_crs
    ...    # CROSS_TYPE=${crosstype}    TYPE__FACILITY=OTU3    PATH-NODE__REVERSE=4

Vch-Create+Delete
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    Create Entity    ${r1_vch_n_ch1}    ADMIN=IS    CHAN-BW=50G    EQLZ-ADMIN=ENABLE
    Create Entity    ${r1_vch_c1_ch1}    ADMIN=IS    CHAN-BW=50G

Vch-Create
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    Create Entity    ${r1_vch_n_ch1}    ADMIN=IS    CHAN-BW=50G    EQLZ-ADMIN=ENABLE
    Create Entity    ${r1_vch_c1_ch1}    ADMIN=IS    CHAN-BW=50G

Crs-Create+Delete
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    ${crs_add}    Set Variable    CRS_CH-${r1_vch_c1_ch1},${r1_vch_n_ch1}
    ${crs_drop}    Set Variable    CRS_CH-${r1_vch_n_ch1},${r1_vch_c1_ch1}
    Create Entity    ${crs_add}    PATH-NODE=1
    Create Entity    ${crs_drop}    PATH-NODE=1    CONFIG__CRS=DROP    TYPE__FACILITY=OPTICAL
    Sleep    10
    Destroy Entity    ${crs_drop}
    Destroy Entity    ${crs_add}

Crs-Create
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    ${crs_add}    Set Variable    CRS_CH-${r1_vch_c1_ch1},${r1_vch_n_ch1}
    ${crs_drop}    Set Variable    CRS_CH-${r1_vch_n_ch1},${r1_vch_c1_ch1}
    Create Entity    ${crs_add}    PATH-NODE=1
    Create Entity    ${crs_drop}    PATH-NODE=1    CONFIG__CRS=DROP    TYPE__FACILITY=OPTICAL

Crs-Set
    ${ch1}    Set Variable    19500
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    ${crs_add}    Set Variable    CRS_CH-${r1_vch_c1_ch1},${r1_vch_n_ch1}
    ${crs_drop}    Set Variable    CRS_CH-${r1_vch_n_ch1},${r1_vch_c1_ch1}
    #    Set Entity Param    ${crs_add}    ADMIN=DSBLD
    #    Set Entity Param    ${crs_drop}    ADMIN=DSBLD
    #    Set Entity Param    MOD-11-7    ADMIN=DSBLD
    #    ${admin}    Get Entity Param    MOD-2-6    ADMIN
    Set Entity Param    MOD-2-18    ADMIN=MT

Crs-Delete
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    ${r2_vch_n_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-N-${ch1}
    ${r2_vch_c2_ch1}    Set Variable    VCH-${r2_sh}-${r2_slot}-C2-${ch1}
    ${crs_add}    Set Variable    CRS_CH-${r1_vch_c1_ch1},${r1_vch_n_ch1}
    ${crs_drop}    Set Variable    CRS_CH-${r1_vch_n_ch1},${r1_vch_c1_ch1}
    #    Destroy Entity    ${crs_drop}
    Destroy Entity    ${crs_add}

Vch-Set
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    Set Entity Param    ${r1_vch_c1_ch1}    ADMIN=MT
    Set Entity Param    ${r1_vch_n_ch1}    ADMIN=MT

Vch-Delete
    ${r1_vch_n_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-N-${ch1}
    ${r1_vch_c1_ch1}    Set Variable    VCH-${r1_sh}-${r1_slot}-C1-${ch1}
    Destroy Entity    ${r1_vch_c1_ch1}
    Destroy Entity    ${r1_vch_c1_ch1}

Om-Delete
    Destroy Entity    ${aid}

Mod-Delete
    Destroy Entity    ${aid}

Sh-Delete
    #    Set Entity Param    FCU-3    ADMIN=DSBLD
    #    Destroy Entity    FCU-3
    Set Entity Param    SHELF-3    ADMIN=MT
    Destroy Entity    SHELF-3

Get
    #    ${admin}    Get Entity Param    MOD-2-6    ADMIN
    #    ${admin}    Get Entity Param    MOD-2-7    ADMIN
    #    ${admin}    Get Entity Param    MOD-2-8    ADMIN
    #    ${type}    Get Entity Param    ${aid}    EP_TYPE__EQUIPMENT
    #    ${type}    Get Entity Param    MOD-2-6    TYPE__EQUIPMENT
    #    ${type}    Get Entity Param    MOD-2-7    TYPE__EQUIPMENT
    ${type}    Get Entity Param    MOD-2-8    TYPE__EQUIPMENT

Mod-Force Delete
    Force Destroy Entity    MOD-11-4

empty
    No Operation

*** Keywords ***
Suite Setup
    [Arguments]    ${name}    ${ip}
    Open Named Connection    ${name}    ${ip}

Suite Teardown
    [Arguments]    ${name}
    Close Connection    ${name}
