"""Global library for NED interface."""

import re
import time

from NEDdriver import NEDdriver


class NEDSession(NEDdriver):
    """NED connection."""

    def __init__(self, host, **options):
        """Open session and login."""
        NEDdriver.__init__(self)
        self.open_connection(host, **options)
        self._get_gissue()
        # set credentials
        if 'login' in options:
            login = options['login']
        else:
            login = 'ADMIN'

        if 'password' in options:
            password = options['password']
        else:
            password = 'CHGME.1a'

        self.ned_login(login, password)

    def close(self):
        """Close NED connection."""
        self.close_connection()

    # ==============
    # Helper Methods
    # ==============
    @staticmethod
    def _otlg_to_lambda(port):
        """Convert OTLG port to lambda.

        :param port: OTLG port
        :return: lambda of the port
        """
        port_to_lambda = {
            '1': '19590',
            '2': '19580',
            '3': '19570',
            '4': '19560',
            '5': '19550',
            '6': '19540',
            '7': '19530',
            '8': '19520',
            '9': '19510',
            '10': '19500',
            '11': '19490',
            '12': '19480',
            '13': '19470',
            '14': '19460',
            '15': '19450',
            '16': '19440',
            '17': '19430',
            '18': '19420',
            '19': '19410',
            '20': '19400',
            '21': '19390',
            '22': '19380',
            '23': '19370',
            '24': '19360',
            '25': '19350',
            '26': '19340',
            '27': '19330',
            '28': '19320',
            '29': '19310',
            '30': '19300',
            '31': '19290',
            '32': '19280',
            '33': '19270',
            '34': '19260',
            '35': '19250',
            '36': '19240',
            '37': '19230',
            '38': '19220',
            '39': '19210',
            '40': '19200',
            '41': '19595',
            '42': '19585',
            '43': '19575',
            '44': '19565',
            '45': '19555',
            '46': '19545',
            '47': '19535',
            '48': '19525',
            '49': '19515',
            '50': '19505',
            '51': '19495',
            '52': '19485',
            '53': '19475',
            '54': '19465',
            '55': '19455',
            '56': '19445',
            '57': '19435',
            '58': '19425',
            '59': '19415',
            '60': '19405',
            '61': '19395',
            '62': '19385',
            '63': '19375',
            '64': '19365',
            '65': '19355',
            '66': '19345',
            '67': '19335',
            '68': '19325',
            '69': '19315',
            '70': '19305',
            '71': '19295',
            '72': '19285',
            '73': '19275',
            '74': '19265',
            '75': '19255',
            '76': '19245',
            '77': '19235',
            '78': '19225',
            '79': '19215',
            '80': '19205'}
        if port in port_to_lambda:
            return port_to_lambda[port]
        return port

    @staticmethod
    def _change_time_period(param, period):
        """Change to YP naming convention."""
        # Change to proper time period
        group = ''
        if period in ['15min', '15MIN']:
            group = '15MIN'
        elif period in ['24HOUR', '24hour', '1DAY', '1day']:
            group = '24HOUR'
        elif period in ['1WEEK', '1week']:
            group = '1WEEK'
        parameter = param + '__%s' % group
        return parameter, group

    @staticmethod
    def str2num(value):
        """Convert string to int or float.

        :param value: string
        :return: number - float or int
        """
        return "." in value and float(value) or int(value)

    @staticmethod
    def severity_trans(severity):
        """Convert NED severity to YP naming convention."""
        sev_dict = {
            "Critical": "CR",
            "Major": "MJ",
            "Minor": "MN",
            "Information": "NA",
            "Not Reported": "NR"}
        return sev_dict[severity]

    @staticmethod
    def sa_trans(effect):
        """Convert NED severity to YP naming convention."""
        sa_dict = {"Not Service Affecting": "NSA", "Service Affection": "SA"}
        return sa_dict[effect]

    def _elapsed_time(self, aid, period):
        """Retrive elapsed time from NED.

        :param aid: channel
        :param period: PM period
        :return: elapsed time
        """
        # Change to proper time period
        loc = ''
        if period in ['15min', '15MIN']:
            loc = 'EP_PM_ELAPSED_TIME_15MIN'
        elif period in ['24HOUR', '24hour', '1DAY', '1day']:
            loc = 'EP_PM_ELAPSED_TIME_1DAY'
        elif period in ['1WEEK', '1week']:
            loc = 'EP_PM_ELAPSED_TIME_1WEEK'
        val = self.get_value(aid, loc)
        # calculate to seconds
        val = sum(
            int(x) * 60 ** i for i,
            x in enumerate(
                reversed(
                    val.split(":"))))
        return val

    def _crypto_officer_change(self, crypto_pw, new_pw=None):
        """Change crypto officer password.

        :param crypto_pw: old password
        :param new_pw: new password
        :return: new password
        """
        # default password doesn't meet requirements
        if crypto_pw == "CHANGEME.1":
            new_pw = "CHANGEME.1A"
        # check if wizard for changing crypto office password is opened
        if "_crypto;passwordChange" in self:
            if not new_pw:
                new_pw = crypto_pw
            self.set_value('crypto', 'current-password', crypto_pw)
            self.set_value('crypto', 'new-password', new_pw)
            self.set_value('crypto', 'confirm-password', new_pw)
            self.try_click("_crypto;passwordChange;apply")
            self._wait_loading()
        return new_pw

    def _clear_pm_counter(self, aid, value):
        """Clear PM counter."""
        # going to Clear Counter tab
        blade = self.seek_parameter(aid, 'EP_RESET_PM_DL_COUNTERS')[1]
        blade = re.sub(r'[^\w]', '', blade).lower()
        # choose PMs type to clear
        loc = "//div[@id='%sClear-Counters']//tr[td='%s']//input[@value='%s']" % (  # noqa: E501
            blade, aid, value)
        self.click(loc)
        # approve
        loc = "//span[@id='%s;clear-counters']" % blade
        self.click(loc)
        response = self._check_status()
        if response:
            raise RuntimeError("Not possible to create %s" % aid)
        return

    def _user_extended_params(self, params):
        """Translate from TL1 naming to NED naming convention.

        :param params: key:value dictionary  or single key
        :return: key:value dictionary or single key with NED naming convention
        """
        ep_params = {
            'UAP': 'EP_PRIVILEGE',
            'PID': 'password',
            'NEW_PID': 'newpassword',
            'UID': 'EP_USER_NAME',
            'TMOUT': 'EP_TL1_TMOUT',
            'TMOUTA': 'EP_TL1_TMOUTA',
            'UISTATE': 'EP_ACCOUNT_STATE_EDIT',
            'SNMP-ACCESS': 'EP_SNMP_SECURITY_LEVEL',
            'PAGE': 'EP_PASSWORD_MAX_AGE',
            'PINT': 'EP_PASSWORD_MIN_AGE',
            'PCND': 'EP_PASSWORD_EXP_WARN_PERIOD',
            'MXINV': 'EP_LOGIN_FAIL_COUNT',
            'UOUT': 'EP_ACCOUNT_INACTIVITY_PERIOD',
            'END-DATE': 'DATE',
            'ACCOUNT_STATE': 'EP_ACCOUNT_STATE_EDIT',
            'ACCESS-DAYS': 'ACCESS-DAYS-LIST',
            'ACCESS-STARTTM': 'ACCESS-STARTTM',
            'ACCESS-ENDTM': 'ACCESS-ENDTM',
            'PASSWORD_LASTCHANGE_DATE': 'EP_PASSWORD_LAST_CHANGE_DATE',
            'FAIL_INFO': 'failLoginMsg',
            'SUCCESS_INFO': 'successLoginMsg',
            'CHGPID': 'EP_USER_PASSWORD_CHANGE'}
        if isinstance(params, dict):
            # convert dictionary to NED naming
            ep_dict = {}
            uistate = {'INH': 'MANUAL_LOCK', 'ALW': 'UNLOCK'}
            for key, value in params.iteritems():
                if key in ep_params:
                    if key == 'UISTATE':
                        value = uistate[value]
                    key = ep_params[key]
                    if key == 'ACCESS-DAYS-LIST':
                        daylist = []
                        for day in value.split('&'):
                            daylist.append(self._jsdata.val2name[key, day])
                        value = '&'.join(daylist)
                    elif (key, value) in self._jsdata.val2name:
                        value = self._jsdata.val2name[key, value]
                    ep_dict[key] = value
                else:
                    raise KeyError
            return ep_dict
        else:
            # convert single key to NED naming
            if params in ep_params:
                key = ep_params[params]
                return key
            else:
                raise KeyError

    # ============================
    # Create Methods
    # ============================
    def create_entity(self, aid, **keys_and_values):
        """Create entity."""
        # try:
        aidtype = aid.split('-')[0]
        # go to entity
        # for other entities proper Add button have to be choosen
        if "FFP_" in aidtype:
            blade = self.seek_parameter(aid, 'WKG-AID')[1]
        else:
            blade = self.seek_parameter(aid, 'EP_AID')[1]

        # to create OM
        if aidtype in ['OM']:
            blade = 'Ports'
            loc = "//span[contains(., '%s')]" % blade
            self.click(loc)
        # to create VCH
        elif aidtype in ['VCH']:
            # to get TYPEEQPT of Mod
            if len(aid.split('-')) >= 2:
                shelf = aid.split('-')[1]
            if len(aid.split('-')) >= 3:
                slot = aid.split('-')[2]
            loc = "//span[@id='_MOD-%s-%s;tree']/span" % (shelf, slot)
            typeeqpt = self.get_value_loc(loc)
            typeeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', typeeqpt]
            # to create VCH of a ROADM/CCM
            if 'ROADM' in typeeqpt or '9CCM' in typeeqpt:
                # firstly clear the drop down filter
                loc = "//*[@id='_opticalchannels;filter']/tbody/tr/td[2]"
                self.click(loc)
                # then check Advanced checkbox; click it if it's not checked
                loc = "//*[@id='showAdvancedPanel']"
                checkbox_state = self[loc].get_attribute('aria-pressed')
                if checkbox_state == 'false':
                    self.click(loc)
                # ready to continue
                blade = 'Optical Channels'

        # open wizard
        bladename = re.sub(r'[^\w]', '', blade).lower()

        if bladename == "":
            loc = "_add"
        else:
            loc = "_%s;add" % bladename
            if aidtype not in ['CH', 'PL', 'UCH']:
                if "_%s;add-network-end-point" % bladename in self:
                    loc = "_%s;add-network-end-point" % bladename
                elif "_%s;add-end-point" % bladename in self:
                    loc = "_%s;add-end-point" % bladename

        self.click(loc)
        # wait for wizard window
        self._wait_loading()
        # choosing slot
        self.choose_slot(aid)
        # parameter queue
        self.param_queue(aid, keys_and_values)
        # add and check
        self.click("_wizard;add")
        self._wait_loading()
        # check compld code
        response = self._check_status()
        self.try_click("//span[@title='Press ESC to close']")
        if response:
            raise RuntimeError("Not possible to create %s" % aid)

        # except Exception as ex:
            # self.try_click("//span[@title='Press ESC to close']")
            # raise ex

    def create_shelf(self, aid, **keys_and_values):
        """Create shelf."""
        try:
            aidtype = aid.split('-')[0]

            self.change_appl('Configure')
            # open wizard
            if aidtype in ['PSH']:
                loc = "_PSHS;tree"
                if loc in self:
                    self.click(loc)
                self._wait_loading()
                self.click("_add")
            else:
                self.click("_NE;tree")
                self._wait_loading()
                self.click("_add;ne")

            # wait for wizard window
            self._wait_loading()
            # choosing slot
            self.choose_slot(aid)
            # parameter queue
            self.param_queue(aid, keys_and_values)
            # add and check
            self.click("_wizard;add")
            # check compld code
            response = self._check_status()
            if response:
                raise RuntimeError("Not possible to create %s" % aid)
            # wait for tree refreshing
            while "_%s;tree" % aid not in self:
                self.driver.implicitly_wait(1)

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def create_module(self, aid, **keys_and_values):
        """Create entity."""
        try:
            shelf = None

            if len(aid.split('-')) >= 2:
                shelf = aid.split('-')[1]

            self.change_appl('Configure')

            # go to entity
            # click on the shelf
            loc = "//span[@id='_SHELF-%s;tree']/span" % shelf
            self._wait_loading(loc)
            self.click(loc)
            # expand tree
            loc = "//span[@id='_SHELF-%s;tree' and @aria-expanded='false']" % \
                shelf
            if loc in self:
                self.click("//img[../span/span[@id='_SHELF-%s;tree']]" % shelf)

            # module is added directly under SHELF
            self._wait_loading()
            self.click("_add")

            # wait for wizard window
            self._wait_loading()
            # choosing slot
            self.choose_slot(aid)
            # parameter queue
            self.param_queue(aid, keys_and_values)
            # add and check
            self.click("_wizard;add")
            # check compld code
            response = self._check_status()
            if response:
                raise RuntimeError("Not possible to create %s" % aid)
            # wait for tree refreshing
            while "_%s;tree" % aid not in self:
                self.driver.implicitly_wait(1)
        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def create_crsch(self, aid, EOU=False, **keys_and_values):
        """Create Cross Connection for channels.

        1 - CRS_CH for WCH/OWLG
        2 - CRS_CH for VCH,CH...
        """
        try:
            (aidfrom, aidto) = str(aid).split('CRS_CH-')[1].split(',')

            aidtype, shelf, module = None, None, None
            behaveto, behavefrom = None, None
            aidtype = aidfrom.split('-')[0]
            aidfromtype = aidfrom.split('-')[0]
            aidtotype = aidto.split('-')[0]
            wiz = 'wizard'

            if len(aidfrom.split('-')) >= 2:
                shelf = aidfrom.split('-')[1]
            if len(aidfrom.split('-')) >= 3:
                module = aidfrom.split('-')[2]

            self.change_appl('Configure')

            # CRS OLS
            if aidtype in ['WCH', 'OWLG'] or aidtotype in ['WCH', 'OWLG']:
                # going to optical lines
                self.click("_OLS;tree")
                blade = 'Optical Channels'

                if self.try_click(
                        "//div[div[span='%s'] " % blade +
                        "and contains(@class,'dijitClosed')]"):
                    self._wait_loading()
                # open wizard
                self.click("_opticalchannels;add-connection")
                self._wait_loading()
                # direction:
                direction = '(A) -> (B)'
                if 'TYPE__CRS' in keys_and_values:
                    if keys_and_values['TYPE__CRS'] == "2WAY":
                        direction = '(A) <-> (B)'
                self.set_value('wizard', 'direction', direction)
                # super channel
                if 'OWLG' in [aidtype, aidtotype]:
                    self.try_click(
                        "//input[@id='_wizard;channel-group'" +
                        " and @aria-pressed='true']")
                # connection type:
                conn_type = 'PassThru'
                if aidtype not in ['WCH', 'OWLG'] or \
                        aidtotype not in ['WCH', 'OWLG']:
                    if aidtype not in ['WCH', 'OWLG']:
                        conn_type = 'Add'
                    else:
                        conn_type = 'Drop'
                    if 'TYPE__CRS' in keys_and_values:
                        if keys_and_values['TYPE__CRS'] == "2WAY":
                            conn_type = 'AddDrop'
                self.click("_wizard;radio%s" % conn_type)
                self._wait_loading()
                # aid from
                self.set_value('wizard', 'optical-line-a', shelf)
                self.set_value('wizard', 'channel-a',
                               '-'.join(aidfrom.split('-')[2:]))
                # aid to
                self.set_value('wizard', 'optical-line-B', aidto.split('-')[1])
                self.set_value('wizard', 'channel-b',
                               '-'.join(aidto.split('-')[2:]))

                # add
                self.click("_wizard;add")
                self._wait_loading()

            # CRS CHs
            else:
                # going to the proper blade
                if aidfromtype in ['CH']:
                    blade = self.seek_parameter(aidto, 'EP_AID')[1]
                else:
                    blade = self.seek_parameter(aidfrom, 'EP_AID')[1]
                self._wait_loading()

                loc = "//span[@id='_MOD-%s-%s;tree']/span" % (shelf, module)
                typeeqpt = self.get_value_loc(loc)
                typeeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', typeeqpt]
                # get channels behave for 10WXC if needed
                if '10WXC' in typeeqpt and aidfromtype == 'CH' and \
                        aidtotype == 'CH':
                    behaveto = self.get_value(aidto, 'BEHAVE')
                    behavefrom = self.get_value(aidfrom, 'BEHAVE')
                    behaveto = self._jsdata.name2val['BEHAVE', behaveto]
                    behavefrom = self._jsdata.name2val['BEHAVE', behavefrom]
                    # go to data channels blade where add connection button is
                    # located
                    blade = self.seek_parameter('V' + aidfrom, 'EP_AID')[1]
                # Video modules
                if typeeqpt == '10TCCSDI10G':
                    directnto = self.get_value(aidto, 'DIRECTN')
                    directnfrom = self.get_value(aidfrom, 'DIRECTN')
                    directnto = self._jsdata.name2val['DIRECTN', directnto]
                    directnfrom = self._jsdata.name2val['DIRECTN', directnfrom]

                # open wizard
                bladename = re.sub(r'[^\w]', '', blade).lower()
                # changes on 06/12/2018: start
                if 'ROADM' not in typeeqpt and '9CCM' not in typeeqpt:
                    # changes on 06/12/2018: end
                    loc = "_%s;add-connection" % bladename
                    self.click(loc)
                    self._wait_loading()

                # two different wizards: first for ROADMs
                if 'ROADM' in typeeqpt or '9CCM' in typeeqpt:
                    # changes on 06/12/2018: start
                    # firstly clear the drop down filter
                    loc = "//*[@id='_opticalchannels;filter']/tbody/tr/td[2]"
                    self.click(loc)

                    if EOU:
                        # for EOU create
                        # ignore "Advanced" checkbox

                        # click "Add"
                        blade = 'Optical Channels'
                        loc = "_%s;add-channel" % bladename
                        self.click(loc)
                        self._wait_loading()

                        # CrossType
                        crosstype_dic = {
                            "2WAY_PASS": 'passThrough',
                            'ADD_DROP': 'addDrop',
                            'STEERABLE_ADDDROP': 'steerableAddDrop',
                            '1WAY_PASS': 'passThru',
                            'ADD': 'add',
                            'DROP': 'drop',
                            'STEERABLE_DROP': 'steerableDrop'
                        }
                        crosstype = crosstype_dic[
                            keys_and_values['CROSS_TYPE']
                        ]
                        # if the element id is "_wizard;crossType"
                        # use self.set_value('wizard', 'crossType', crosstype)
                        idname = "_wizard:crossType"
                        self.click(idname)
                        loc = "//div[@id='%s_menu']/table/tbody/\
                            tr/td/img[@alt='%s']" % (idname, crosstype)
                        self.click(loc)
                        self._wait_loading()

                        # Local Port
                        script = \
                            "return window.webgui.wizard.localAid2label['%s']" % \
                            aidfrom
                        locallabel = self.driver.execute_script(script)
                        self.set_value('wizard', 'fromPoint', locallabel)

                        # Linked Port
                        # script = \
                        #     "return window.webgui.wizard.linkedAid2label['%s']" % \
                        #     aidto
                        # linkedlabel = self.driver.execute_script(script)
                        # self.set_value('wizard', 'toPoint', linkedlabel)

                        # channel number
                        ch_no = aidfrom.split('-')[-1]
                        self.set_value('NE', 'CHANNEL__PROVISION', ch_no)

                        # channel bandwidth: not settable

                        # Facility type: default value 'Optical'
                        if 'TYPE__FACILITY' in keys_and_values:
                            type_fac = self._jsdata.val2name[
                                'TYPE__FACILITY',
                                keys_and_values['TYPE__FACILITY']
                            ]
                            self.set_value('NE', 'TYPE__FACILITY', type_fac)

                        # Path node
                        if 'PATH-NODE' in keys_and_values:
                            self.set_value(
                                'NE', 'PATH-NODE',
                                keys_and_values['PATH-NODE'])
                        crosstype_2way = [
                            'passThrough', 'addDrop', 'steerableAddDrop']
                        if crosstype in crosstype_2way:
                            if 'PATH-NODE__REVERSE' in keys_and_values:
                                self.set_value(
                                    'NE', 'PATH-NODE__REVERSE',
                                    keys_and_values['PATH-NODE__REVERSE'])

                        # User Label: default value ''
                        if 'ALIAS' in keys_and_values:
                            self.set_value(
                                'NE', 'ALIAS',
                                keys_and_values['ALIAS'])
                        return True

                    else:
                        # for Advanced creation
                        # then check Advanced checkbox
                        # click it if it's not checked
                        loc = "//*[@id='showAdvancedPanel']"
                        checkbox_state = self[loc].get_attribute('aria-pressed')
                        if checkbox_state == 'false':
                            self.click(loc)
                        # click "Add Connection"
                        blade = 'Optical Channels'
                        loc = "_%s;add-connection" % bladename
                        self.click(loc)
                        self._wait_loading()
                        # changes on 06/12/2018: end
                        # direction:
                        direction = '(A) -> (B)'
                        if 'TYPE__CRS' in keys_and_values:
                            if keys_and_values['TYPE__CRS'] == "2WAY":
                                direction = '(A) <-> (B)'
                        self.set_value('wizard', 'direction', direction)

                        # super channel
                        if aidtype == 'OTLG':
                            loc = "//input[@id='wizard;channel-group' and " + \
                                "(not (@aria-pressed) or @aria-pressed='false')]"
                            self.try_click(loc)

                        # connection type:
                        # helpers variables
                        if len(aidfrom.split('-')) >= 4:
                            port_from = aidfrom.split('-')[3]
                        if len(aidto.split('-')) >= 4:
                            port_to = aidto.split('-')[3]

                        conn_type = 'passThru'
                        if not ("N" in port_from[0] and "N" in port_to[0]):
                            if port_from[0] == "C" and port_to[0] == "N":
                                conn_type = 'add'
                            else:
                                conn_type = 'drop'
                            # AddDrop
                            if 'TYPE__CRS' in keys_and_values:
                                if keys_and_values['TYPE__CRS'] == "2WAY":
                                    conn_type = 'addDrop'

                        if not aidfrom.split("-")[2:3] == aidto.split("-")[2:3]:
                            conn_type = 'steerable%s' % conn_type.capitalize()

                        self.click("%sRadio" % conn_type)
                        self._wait_loading()

                        # Channel number
                        ch_no = aidfrom.split('-')[-1]  # for VCH and new OTLG
                        if aidtype == 'OTLG':
                            if port_from[0] in ['C', 'N']:
                                ch_no = self._otlg_to_lambda(port_to[1:])
                        self.set_value('wizard', 'channelNumber', ch_no)

                        # Local Port
                        script = \
                            "return window.webgui.wizard.localAid2label['%s']" % \
                            aidfrom
                        locallabel = self.driver.execute_script(script)
                        self.set_value('wizard', 'localPort', locallabel)

                        # Linked Port
                        script = \
                            "return window.webgui.wizard.linkedAid2label['%s']" % \
                            aidto
                        linkedlabel = self.driver.execute_script(script)
                        # fix on 6/26/2018: start
                        # self.set_value('wizard', 'localPort', linkedlabel)                    
                        self.set_value('wizard', 'linkedPort', linkedlabel)
                        # fix on 6/26/2018: end

                        # Facility
                        if 'TYPE__FACILITY' in keys_and_values:
                            type_fac = self._jsdata.val2name[
                                'TYPE__FACILITY',
                                keys_and_values['TYPE__FACILITY']
                            ]
                            self.set_value(aid, 'TYPE__FACILITY', type_fac)

                        # Path node
                        self.set_value(
                            aid, 'PATH-NODE', keys_and_values['PATH-NODE'])
                        if 'TYPE__CRS' in keys_and_values:
                            if keys_and_values['TYPE__CRS'] == "2WAY":
                                return_aid = "CRS_CH-%s,%s" % (aidto, aidfrom)
                                self.set_value(
                                    return_aid, 'PATH-NODE',
                                    keys_and_values['PATH-NODE'])
                elif typeeqpt == '10WXC10G':
                    # helpers variables
                    port_from = aidfrom.split('-')[3]
                    port_to = aidto.split('-')[3]

                    if behaveto == "CLIENT" and behavefrom == "CLIENT":
                        conn_type = 'protectedtwoway'
                    elif 'VCH' in aidtotype and 'VCH' in aidfromtype:
                        conn_type = 'pass-through'
                    else:
                        conn_type = 'add-drop'
                    # choose type of connection
                    self.click('_%s;%s' % (wiz, conn_type))

                    # Aid from:
                    self.set_value(wiz, '(a)port', port_from)
                    self.set_value(wiz, '(a)endpoint', aidfrom)

                    # Aid to:
                    self.set_value(wiz, '(b)port', port_to)
                    self.set_value(wiz, '(b)endpoint', aidto)
                elif typeeqpt == '10TCCSDI10G':
                    pass
                else:
                    # helpers variables
                    port_from = aidfrom.split('-')[-1]
                    port_to = aidto.split('-')[-1]

                    # direction
                    conn_type = 'passThru'
                    if not ("N" in aidfrom and "N" in aidto):
                        conn_type = 'addDrop'
                        if "C" in port_from and "C" in port_to:
                            # Hairpin
                            conn_type = 'localC2C'
                    self.click("%sRadio" % conn_type)
                    self._wait_loading()

                    # Aid from:
                    self.set_value('wizard', 'EndPoint1', aidfrom)
                    # Aid to:
                    self.set_value('wizard', 'EndPoint2', aidto)

                    # ID for exlicit aid
                    return_aid = "CRS_CH-%s,%s" % (aidto, aidfrom)
                    # connection type
                    if 'TYPE__CRS' in keys_and_values:
                        type_crs = self._jsdata.val2name[
                            'TYPE__CRS', keys_and_values['TYPE__CRS']]
                        try:
                            self.set_value(aid, 'TYPE__CRS', type_crs)
                        except Exception:
                            self.set_value(return_aid, 'TYPE__CRS', type_crs)

                    # connection
                    if 'CONN' in keys_and_values:
                        conn = self._jsdata.val2name[
                            'CONN', keys_and_values['CONN']]
                        try:
                            self.set_value(aid, 'CONN', conn)
                        except Exception:
                            self.set_value(return_aid, 'CONN', conn)

                # Clicking ADD:
                # self.click('_%s;add' % wiz)
                # self._wait_loading()

                # click Cancel
                self.click('_%s;cancel' % wiz)
                self._wait_loading()                

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def create_crsdcn(self, aid, **keys_and_values):
        """Create entity."""
        try:
            # go to entity
            blade = self.seek_parameter(keys_and_values['LINK'], 'EP_AID')[1]
            # open wizard
            bladename = re.sub(r'[^\w]', '', blade).lower()

            self.click("_%s;add-connection" % bladename)
            # wait for wizard window
            self._wait_loading()
            # choosing LINK
            self.set_value('wizard', 'link', keys_and_values['LINK'])
            # choose ECC
            self.set_value('wizard', 'ecc', keys_and_values['ECC'])
            # add and check
            self.click("_wizard;add")
            self._wait_loading()
            # check compld code
            response = self._check_status()
            self.try_click("//span[@title='Press ESC to close']")
            if response:
                raise RuntimeError("Not possible to create %s" % aid)

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def create_ol(self, aid, **keys_and_values):
        """Create optical line.

        OL, WCH, OWLG
        """
        try:
            aidtype = aid.split('-')[0]

            self.change_appl('Configure')
            self.click("_OLS;tree")
            self._wait_loading()
            # open wizard
            if aidtype == 'OL':
                self.click("_add")
            else:
                loc = "//div[div[span='Optical Channels'] and " + \
                    "contains(@class,'dijitClosed')]"
                self.try_click(loc)
                self._wait_loading()
                self.click("_opticalchannels;add-end-point")
            # wait for wizard window
            self._wait_loading()
            # choosing slot
            self.choose_slot(aid)
            self._wait_loading()
            # parameter queue
            if keys_and_values:
                self.param_queue(aid, keys_and_values)
            # add and check
            self.click("_wizard;add")
            # check compld code
            response = self._check_status()
            self.try_click("//span[@title='Press ESC to close']")
            if response:
                raise RuntimeError("Not possible to create %s" % aid)

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def create_flw(self, aid, **keys_and_values):
        """Create FLW."""
        try:
            port = 'ETH-' + '-'.join(aid.split('-')[1:-1])
            eth = aid.split('-')[-2]
            svid = re.sub(r'[\D]', '', aid.split('-')[-1])

            # go to entity
            if 'TYPE__FACILITY' not in keys_and_values:
                blade = self.seek_parameter(aid, 'EP_AID')[1]
            else:
                if keys_and_values['TYPE__FACILITY'] == 'ELAN':
                    blade = self.seek_parameter(aid, 'BRIDGE')[1]
                else:
                    blade = self.seek_parameter(aid, 'EP_AID')[1]

            # open wizard
            bladename = re.sub(r'[^\w]', '', blade).lower()
            loc = "_%s;add" % bladename
            self.click(loc)
            # wait for wizard window
            self._wait_loading()

            # choosing SVID
            elem = self['inputServiceID']
            elem.clear()
            elem.send_keys('%s' % svid)
            self._wait_loading()
            self.try_click(
                "//input[@id='checkboxProtected' and @aria-pressed='false']")
            # chechboxes are refreshing after SVID change
            time.sleep(2)

            # select port
            # if it's protected port:
            loc = "//ul[@class='summaryList']//" + \
                "input[contains(@id,'ports') and @aria-pressed='true']"
            ports_choosen = self.driver.find_elements_by_xpath(loc)
            if len(ports_choosen) == 2:
                # FLWs and CRS FLWs are created
                # select wrk and protn ports:
                wkg = [
                    'select2protect',
                    ports_choosen[0].get_attribute('value')]
                protn = ['select4protection', port]
                for select, value in [wkg, protn]:
                    loc = "//table[@id='%s']" % select
                    self.click(loc)
                    loc = "//div[@id='%s_menu']/table/tbody/tr[td='%s']" % (
                        select, value)
                    if loc in self:
                        self[loc].location_once_scrolled_into_view
                        self.click(loc)

            # first flow/crsflw
            else:
                loc = "//ul[@class='summaryList']//" + \
                    "input[contains(@value,'%s')]" % port
                elem = self[loc]
                try:
                    if elem.get_attribute('aria-disabled') != 'true':
                        # wait for checkbox activation
                        elem = self[loc]
                except Exception:
                    elem = self[loc]
                if elem.get_attribute('aria-disabled') == 'false' and \
                   elem.get_attribute('aria-pressed') != 'true':
                    elem.click()
                else:
                    raise Exception

            # parameter queue
            if keys_and_values:
                self.param_queue(aid, keys_and_values)
            # add and check
            self.click("//span[contains(@id, '_wizard;add-%s')]" % eth)
            self._wait_loading()
            # check compld code
            response = self._check_status()
            self.try_click("//span[@title='Press ESC to close']")
            if response:
                raise RuntimeError("Not possible to create %s" % aid)

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def create_crsflw(self, aid, **keys_and_values):
        """Create CRS_FLW."""
        try:
            if len(keys_and_values) > 0:
                raise KeyError
            (aidfrom, aidto) = str(aid).split('CRS_FLW-')[1].split(',')

            port_to = 'ETH-' + '-'.join(aidfrom.split('-')[1:-1])
            port_from = 'ETH-' + '-'.join(aidto.split('-')[1:-1])
            eth_from = aidfrom.split('-')[-2]
            eth_to = aidto.split('-')[-2]
            svid = re.sub(r'[\D]', '', aidfrom.split('-')[-1])

            # check if SVID is the same
            if svid != re.sub(r'[\D]', '', aidto.split('-')[-1]):
                raise Exception('SVID should be the same for both FLW')

            # go to entity
            blade = self.seek_parameter(aidto, 'EP_AID')[1]

            # open wizard
            bladename = re.sub(r'[^\w]', '', blade).lower()
            loc = "_%s;add" % bladename
            self.click(loc)
            # wait for wizard window
            self._wait_loading()

            # choosing SVID
            elem = self['inputServiceID']
            elem.clear()
            elem.send_keys('%s' % svid)
            self._wait_loading()
            self.try_click(
                "//input[@id='checkboxProtected' and @aria-pressed='false']")
            # chechboxes are refreshing after SVID change
            time.sleep(2)

            # select port
            # if it's protected port:
            loc = "//ul[@class='summaryList']//input[contains(@id,'ports')" + \
                " and @aria-pressed='true']"
            ports = self.driver.find_elements_by_xpath(loc)
            ports_choosen = []
            for param in ports:
                ports_choosen.append(param.get_attribute('value'))
            if len(ports_choosen) == 2:
                # FLWs and CRS FLWs are created
                # select wrk and protn ports:
                ports_choosen.remove(port_to)
                wkg = ['select2protect', ports_choosen[0]]
                protn = ['select4protection', port_from]
                for select, value in [wkg, protn]:
                    loc = "//table[@id='%s']" % select
                    select_tab = self[loc]
                    if select_tab.text != value:
                        select_tab.click()
                        loc = "//div[@id='%s_menu']" % select + \
                            "/table/tbody/tr[td='%s']" % value
                        if loc in self:
                            self.click(loc)
                        else:
                            try:
                                loc = "//div[@id='%s_menu']" % select + \
                                    "/table/tbody/tr[td='%s']" % port_from
                                self.click(loc)
                            except Exception:
                                loc = "//div[@id='%s_menu']" % select + \
                                    "/table/tbody/tr[td='%s']" % \
                                    ports_choosen[0]
                                self.click(loc)
            else:
                for port in [port_from, port_to]:
                    loc = "//ul[@class='summaryList']" + \
                        "//input[contains(@value,'%s')]" % port
                    elem = self[loc]
                    try:
                        if elem.get_attribute('aria-disabled') != 'true':
                            # wait for checkbox activation
                            elem = self[loc]
                    except Exception:
                        elem = self[loc]
                    if elem.get_attribute('aria-disabled') == 'false' and \
                       elem.get_attribute('aria-pressed') != 'true':
                        elem.click()
                    else:
                        raise Exception
            time.sleep(1)

            # add and check
            try:
                self.click(
                    "//span[contains(@id, '_wizard;add-%s%s')]" %
                    (eth_from, eth_to))
            except Exception:
                self.click(
                    "//span[contains(@id, '_wizard;add-%s%s')]" %
                    (eth_to, eth_from))
            self._wait_loading()
            # check compld code
            response = self._check_status()
            self.try_click("//span[@title='Press ESC to close']")
            if response:
                raise RuntimeError("Not possible to create %s" % aid)

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def create_ffpflw(self, aid, **keys_and_values):
        """Create FFP_FLW."""
        try:
            svid = re.sub(r'[\D]', '', aid.split('-')[-1])

            try:
                port_wkg = keys_and_values['WKG-AID']
                port_protn = keys_and_values['PROTN-AID']
                eth_wkg = 'ETH-' + '-'.join(port_wkg.split('-')[1:-1])
                eth_protn = 'ETH-' + '-'.join(port_protn.split('-')[1:-1])
            except Exception:
                raise Exception("Missing AIDs")

            # check if SVID is the same
            if svid != re.sub(r'[\D]', '', aid.split('-')[-1]):
                raise Exception('SVID should be the same for both FLW')

            # go to entity
            blade = self.seek_parameter(aid, 'WKG-AID')[1]

            # open wizard
            bladename = re.sub(r'[^\w]', '', blade).lower()
            loc = "_%s;add" % bladename
            self.click(loc)
            # wait for wizard window
            self._wait_loading()

            # choosing SVID
            elem = self['inputServiceID']
            elem.clear()
            elem.send_keys('%s' % svid)
            self._wait_loading()
            self.try_click(
                "//input[@id='checkboxProtected' and @aria-pressed='false']")
            # chechboxes are refreshing after SVID change
            time.sleep(2)

            # select port
            # eth wkg
            loc = "//ul[@class='summaryList']" + \
                "//input[contains(@value,'%s')]" % eth_wkg
            elem = self[loc]
            try:
                if elem.get_attribute('aria-disabled') != 'true':
                    # wait for checkbox activation
                    elem = self[loc]
            except Exception:
                elem = self[loc]
            if elem.get_attribute('aria-disabled') == 'false' and \
               elem.get_attribute('aria-pressed') != 'true':
                elem.click()
            else:
                raise Exception

            # protn wkg
            loc = "//ul[@class='summaryList']" + \
                "//input[not(contains(@value,'%s')) " % eth_protn + \
                "and not(@aria-pressed='true')]"

            elem = self[loc]
            try:
                if elem.get_attribute('aria-disabled') != 'true':
                    # wait for checkbox activation
                    elem = self[loc]
            except Exception:
                elem = self[loc]
            if elem.get_attribute('aria-disabled') == 'false' and \
               elem.get_attribute('aria-pressed') != 'true':
                elem.click()
            else:
                raise Exception
            time.sleep(1)

            # select wrk and protn ports:
            wkg = ['select2protect', eth_wkg]
            protn = ['select4protection', eth_protn]
            for select, value in [wkg, protn]:
                loc = "//table[@id='%s']" % select
                select_tab = self[loc]
                if select_tab.text != value:
                    select_tab.click()
                    loc = "//div[@id='%s_menu']/table/tbody/tr[td='%s']" % (
                        select, value)
                    if loc in self:
                        self.click(loc)
                    else:
                        try:
                            # TODO
                            loc = "//div[@id='%s_menu']" % select + \
                                "/table/tbody/tr[td='%s']" % eth_wkg
                            self.click(loc)
                        except Exception:
                            loc = "//div[@id='%s_menu']" % select + \
                                "/table/tbody/tr[td='%s']" % eth_protn
                            self.click(loc)
            time.sleep(1)
            # setting domain
            try:
                mdom = keys_and_values['LEVEL__MD-MONITORED']
                loc = "//div[../div[label='Domain Level: ']" + \
                    " and @class='paramWidget']/table"
                loc_id = self[loc].get_attribute('id')
                loc = "//table[@id='%s']" % loc_id
                self.click(loc)
                loc = "//div[@id='%s_menu']/table/tbody/tr[td='%s']" % (
                    loc_id, mdom)
                if loc in self:
                    self.click(loc)
            except Exception:
                raise Exception("Missing parameters")
            # add and check
            self.click("//span[@id='_wizard;add-FFP']")
            self._wait_loading()
            # check compld code
            response = self._check_status()
            self.try_click("//span[@title='Press ESC to close']")
            if response:
                raise RuntimeError("Not possible to create %s" % aid)

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def create_ech(self, aid, **keys_and_values):
        """Create ECH.

        OL, WCH, OWLG
        """
        try:
            self.change_appl('Configure')
            self.click("_ECI;tree")
            self._wait_loading()
            # open wizard
            if not self.try_click("_externalchannels;add"):
                self.click("_add")
            # wait for wizard window
            self._wait_loading()
            # choosing slot
            self.choose_slot(aid)
            self._wait_loading()
            # choosing eci profile
            if 'FILE' in keys_and_values:
                keys_and_values['EP_PROFILE_NAME'] = keys_and_values['FILE']
                keys_and_values.pop('FILE')
            # parameter queue
            if keys_and_values:
                self.param_queue(aid, keys_and_values)
            # add and check
            self.click("_wizard;add")
            # check compld code
            response = self._check_status()
            self.try_click("//span[@title='Press ESC to close']")
            if response:
                raise RuntimeError("Not possible to create %s" % aid)

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

# exceptions TODO:
    def create_otlg(self, aid, **keys_and_values):
        """Create OTLG.

        OTLG
        """
        raise NotImplementedError

    def create_conn(self, aid, **keys_and_values):
        """Create Connection.

        # WhichTab, tableName = seekParameter(aid, 'WKG-AID', sel)
        """
        raise NotImplementedError

    def create_ntpsrv(self, aid, **keys_and_values):
        """Create Network Time Protocoll server.

        NTP
        """
        raise NotImplementedError

    # ============================
    # Get Methods
    # ============================

    def get_param(self, aid, param):
        """Get parameter from entities."""
        # Extended parameters in NE
        if param in ['OPT', 'OPR', 'OSCOPT', 'OSCPWR', 'CAP__PROVISION']:
            param = 'EP_' + param

        # try:
        # finding parameter
        blade = self.seek_parameter(aid, param)[1]
        # FORCED ADMIN modification
        if blade is None and param == 'ADMIN':
            # param = 'EP_ADMIN_FORCED'
            self.seek_parameter(aid, param, edit=False)

        # self._wait_loading()
        try:
            value = self.get_value(aid, param)
        except Exception:
            if param == "ADMIN":
                value = self.get_value(aid, 'EP_ADMIN_FORCED')
            elif param == 'TYPE__EQUIPMENT':
                value = self.get_value(aid, 'EP_TYPE__EQUIPMENT_VARIANT')
            else:
                raise

        # Extended parameters exception:
        if param == "EP_CAP__PROVISION":
            value = "Level " + value.split(":")[0]
            param = "CAP__PROVISION"
        # change NED name to YP
        if (param, value) in self._jsdata.name2val:
            value = self._jsdata.name2val[param, value]

        # close detail window if needed
        self.try_click("//span[@title='Press ESC to close']")

        return value
        # except Exception as ex:
        # self.try_click("//span[@title='Press ESC to close']")
        # raise ex

    def get_param_remauth(self, aid, param):
        """Get parameter from REMAUTH entity."""
        try:
            self.seek_parameter(aid, param)
            value = self.get_value(str(int(aid[-1]) - 1) + aid, param)
            # change NED name to YP
            if (param, value) in self._jsdata.name2val:
                value = self._jsdata.name2val[param, value]
            return value
        except Exception as ex:
            raise ex

    def get_param_crsdcn(self, aid, param):
        """Get parameter from REMAUTH entity."""
        try:
            self.seek_parameter('LINK-' + aid[8:], param)
            loc = "//td[span[@id[contains(.,'_%s')]]]" % aid
            self.try_click(loc)
            self._wait_loading()
            value = self.get_value(aid, param)
            # change NED name to YP
            if (param, value) in self._jsdata.name2val:
                value = self._jsdata.name2val[param, value]
            # close detail window if needed
            self.try_click("//span[@title='Press ESC to close']")
            return value
        except Exception as ex:
            raise ex

    def get_param_crsch(self, aid, param):
        """Get parameter from entities."""
        try:
            (aidfrom, aidto) = str(aid).split('CRS_CH-')[1].split(',')
            aidfromtype = aidfrom.split('-')[0]

            # going to the proper blade
            if aidfromtype in ['CH']:
                blade = self.seek_parameter(aidto, 'EP_AID')[1]
            else:
                blade = self.seek_parameter(aidfrom, 'EP_AID')[1]

            # FORCED ADMIN modification
            if blade is None and param == 'ADMIN':
                param = 'EP_ADMIN_FORCED'
                if aidfromtype in ['CH']:
                    self.seek_parameter(aidto, param)
                else:
                    self.seek_parameter(aidfrom, param)
            self._wait_loading()

            # opening detail window of CRS
            loc = "//td[span[@id[contains(.,'_%s')]]]" % aid
            self.try_click(loc)
            self._wait_loading()

            value = self.get_value(aid, param)

            # change NED name to YP
            if (param, value) in self._jsdata.name2val:
                value = self._jsdata.name2val[param, value]

            # close detail window if needed
            self.try_click("//span[@title='Press ESC to close']")

            return value
        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def get_param_eqpt(self, aid, param):
        """Return Equipment parameter."""
        # going to the proper blade
        self.seek_parameter(aid, param)
        subaid = aid.split("-", 2)[2]
        # read param from table if doesn't occur in details
        if param in ['BOOT__STATUS', 'SA-STBY']:
            # harcoded map of FWP table (IDs are still missing)
            fwpmap = {
                'FWPREV': '3',
                'FWPREV-STBY': '4',
                'FWPREV-SYS-ACT': '5',
                'ACTIVATION_READY': '6',
                'SA': '7',
                'FWPREV-SYS-STBY': '8',
                'ACTIVATION_STBY_SW_READY': '9',
                'SA-STBY': '10',
                'PROTECTION': '11',
                'BOOT__STATUS': '12'}
            cell = fwpmap[param]
            loc = "//tr[td[text()='%s']]/td[%s]" % (subaid, cell)
            value = self.get_value_loc(loc)
        else:
            # open details
            loc = "//tr[td[text()='%s']]" % subaid
            self.click(loc)
            self._wait_loading()
            value = self.get_value(aid, param)

        # change NED name to YP
        if (param, value) in self._jsdata.name2val:
            value = self._jsdata.name2val[param, value]

        return str(value)
        # except Exception as ex:
        # self.try_click("//span[@title='Press ESC to close']")
        # raise ex

    def get_param_copy(self, aid, param):
        # going to the proper blade
        self.seek_parameter(aid, param)
        if param != "BACKUPFILE":
            return False
        # retrive DBS filename
        loc = "//table[@class='dojoxGridRowTable']" + \
            "/tbody/tr/td[contains(.,'.DBS')]"
        filename = self.get_value_loc(loc)

        return filename

    def get_param_srv(self, aid, param):
        """Get parameter from entities."""
        # try:
        # finding parameter
        self.seek_parameter(aid, param)
        if param == 'INSTALL__STATE':
            text = self._jsdata.val2name[
                'EP_UBRSERVER_BUSY_STATE', 'SW_INSTALL']
            # wait for progress bar:
            count = 0
            inf = "//div[contains(@class,'nodeMessage')" + \
                " and contains(@style,'opacity: 1')]"
            while count < 10:
                count += 1
                if inf in self:
                    break
            else:
                value = 'IDLE'
                return value
            # get part of the status bar
            loc = "%s//span[contains(.,'%s')]" % (inf, text)
            # get whole status
            value = self.get_value_loc(loc)
            # get install status
            value = value.split(':')[1][1:]
        elif param in ['GDBISSUE', 'CRDAT', 'CRTM']:
            # get value from the CON file:
            part = aid.split('-')[2]
            loc = "//span[contains(@id,'%s') and contains(@id,'%s')]" % \
                (part, param)
            value = self.get_value_loc(loc)
        else:
            self._wait_loading()
            value = self.get_value(aid, param)

        # change NED name to YP
        if (param, value) in self._jsdata.name2val:
            value = self._jsdata.name2val[param, value]

        return value
        # except Exception as ex:
        # self.try_click("//span[@title='Press ESC to close']")
        # raise ex

    # ============================
    # Destroy Methods
    # ============================
    def destroy_entity(self, aid, force=False):
        """Destroy entity."""
        # try:

        self.seek_parameter(aid, 'EP_AID')
        self._wait_loading()

        # open entity details
        if "_wizard;delete" not in self:
            loc = "//td[span[@id[contains(.,'_%s')]]]" % aid
            self.try_click(loc)
            self._wait_loading()
        if 'FFP' in aid and "_wizard;delete" not in self:
            # different ID of FFP entity
            if 'NE' in aid:
                loc = "//td[span[@id[contains(.,'_%s')]]]" % \
                    aid.replace('NE', 'NW')
            elif 'NW' in aid:
                loc = "//td[span[@id[contains(.,'_%s')]]]" % \
                    aid.replace('NW', 'NE')
            self.try_click(loc)
            self._wait_loading()

        # click delete button
        self.click("_wizard;delete")
        self._wait_loading()

        # Force destroy
        if force:
            loc = "%s_forceDelete" % aid
            self.try_click(loc)
        if self._gissue < 15:
            # Approve destroying entity
            loc = "_entity;delete;apply"
        elif self._gissue > 15:
            # Approve destroying entity
            val = 'delete'
            loc = "//*[substring(@id, string-length(@id) - " + \
                "string-length('%s')+1) = '%s']" % (val, val)
        self.click(loc)
        self._wait_loading()

        # check compld code
        response = self._check_status()
        if response:
            raise RuntimeError("Not possible to destroy %s" % aid)
        # except Exception as ex:
            # self.try_click("//span[@title='Press ESC to close']")
            # raise ex

    def destroy_passiveshelf(self, aid, force=False):
        """Destroy entity."""
        try:
            self.change_appl('Configure')
            # open wizard
            loc = "//span[@id='_PSHS;tree' and @aria-expanded='false']"
            if loc in self:
                self.click("//img[../span/span[@id='_PSHS;tree']]")
                self._wait_loading()

            # choose Delete from context menu
            self.context_menu(aid, 'Delete')
            self._wait_loading()

            # Force destroy
            if force:
                loc = "%s_forceDelete" % aid
                self.try_click(loc)

            # Approve destroying entity
            if self._gissue < 15:
                # Approve destroying entity
                loc = "_entity;delete;apply"
            elif self._gissue > 15:
                # Approve destroying entity
                val = 'delete'
                loc = "//*[substring(@id, string-length(@id) - " + \
                    "string-length('%s')+1) = '%s']" % (val, val)
            self.click(loc)
            # check compld code
            response = self._check_status()
            if response:
                raise RuntimeError("Not possible to destroy %s" % aid)

        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def destroy_crsdcn(self, aid, force=False):
        """Destroy entity."""
        try:
            self.seek_parameter('LINK-' + aid[8:], 'EP_AID')
            # open entity details
            if "_wizard;delete" not in self:
                loc = "//td[span[@id[contains(.,'_%s')]]]" % aid
                self.try_click(loc)
                self._wait_loading()

            # click delete button
            self.click("_wizard;delete")
            self._wait_loading()

            # Force destroy
            if force:
                loc = "%s_forceDelete" % aid
                self.try_click(loc)

            if self._gissue < 15:
                # Approve destroying entity
                loc = "_entity;delete;apply"
            elif self._gissue > 15:
                # Approve destroying entity
                val = 'delete'
                loc = "//*[substring(@id, string-length(@id) - " + \
                    "string-length('%s')+1) = '%s']" % (val, val)
            self.click(loc)
            self._wait_loading()
            # check compld code
            response = self._check_status()
            if response:
                raise RuntimeError("Not possible to destroy %s" % aid)
        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def destroy_crsch(self, aid, force=False):
        """Destroy CRS CH entity."""
        try:
            (aidfrom, aidto) = str(aid).split('CRS_CH-')[1].split(',')
            aidfromtype = aidfrom.split('-')[0]

            # going to the proper blade
            if aidfromtype in ['CH']:
                self.seek_parameter(aidto, 'EP_AID')
            else:
                self.seek_parameter(aidfrom, 'EP_AID')
            self._wait_loading()

            # changes on 06/12/2018: start
            # for ROADM/CCM
            if aidfromtype in ['VCH']:
                # firstly clear the drop down filter
                loc = "//*[@id='_opticalchannels;filter']/tbody/tr/td[2]"
                self.click(loc)
                # then pick the port
                port_from = aidfrom.rpartition('-')[0].replace('VCH', 'OM')
                self.set_value('opticalchannels', 'filter', port_from)

                # expand the channel
                loc = "//span[@id='_%s;CHANNEL__PROVISION']/../div[\
                    contains(@id, 'dojox_grid__Expando')]" % aidfrom
                self.click(loc)
            # changes on 06/12/2018: end

            # opening detail window of CRS
            loc = "//td[span[@id[contains(.,'_%s')]]]" % aid
            self.click(loc)
            self._wait_loading()

            # click delete button
            self.click("_wizard;delete")
            self._wait_loading()

            # Force destroy
            if force:
                loc = "%s_forceDelete" % aid
                self.try_click(loc)

            # Approve destroying entity
            if self._gissue < 15:
                # Approve destroying entity
                loc = "_entity;delete;apply"
            elif self._gissue > 15:
                # Approve destroying entity
                val = 'delete'
                loc = "//*[substring(@id, string-length(@id) - " + \
                    "string-length('%s')+1) = '%s']" % (val, val)
            self.click(loc)
            self._wait_loading()

            # check compld code
            response = self._check_status()
            if response:
                raise RuntimeError("Not possible to destroy %s" % aid)
        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    # ============================
    # Set Methods
    # ============================

    def set_entity_param(self, aid, key, value):
        """Set entity."""
        # try:
        if key == "PM-RESET__DL":
            return self._clear_pm_counter(aid, value)

        aidtype = aid.split('-')[0]
        # Extended parameters modification
        ep_params = {
            'INHSWTOPROTN': 'EP_PROTECTION_INHSWTO_PARTNER',
            'CDC__OPERATION': 'EP_CDC_OPR_AND_CONDITION',
            'OPR-EQLZ': 'EP_EQLZ_OPR_AND_CONDITION',
            'TURNUP__OPERATION': 'EP_TURNUP_OPR_AND_CONDITION',
            'OPR-LOSATT': 'EP_LOSATT_OPR_AND_CONDITION',
            'ASETAB__OPERATION': 'EP_ASETAB_OPR_AND_CONDITION',
            'CAP__PROVISION': 'EP_CAP__PROVISION'}
        if key in ep_params:
            key = ep_params[key]

        # find parameter location
        applname, blade = self.seek_parameter(aid, key, edit=True)
        # FORCED ADMIN modification
        if blade is None and key == 'ADMIN':
            key = 'EP_ADMIN_FORCED'
            applname, blade = self.seek_parameter(aid, key, edit=True)
        bladename = re.sub(r'[^\w]', '', blade).lower()
        # change value to NED naming
        if (key, value) in self._jsdata.val2name:
            value = self._jsdata.val2name[key, value]
        try:
            if value == self.get_value(aid, key):
                self.try_click("//span[@title='Press ESC to close']")
                self.try_click("//a[contains(@id,';cancel')]")
                return
            self.set_value(aid, key, value)
        except Exception:
            # FORCED ADMIN modification
            if key == 'ADMIN':
                try:
                    self.set_value(aid, 'EP_ADMIN_FORCED', value)
                except Exception:
                    self.try_click("//a[contains(@id,';cancel')]")
                    raise Exception
            else:
                self.try_click("//a[contains(@id,';cancel')]")
                raise Exception

        # change back key name to YP name
        if key in ep_params.values():
            key = dict((v, k) for k, v in ep_params.iteritems())[key]

        # Approve setting parameter
        if applname == 'Maintain':
            if 'Port' in blade:
                self.try_click("_ports;apply")
            else:
                self.try_click("_simple;apply")
        else:
            loc = "_wizard;apply-exit"
            if not self.try_click(loc):
                if aidtype in ['MOD', 'SHELF']:
                    loc = "_simple;apply-exit"
                else:
                    loc = "_%s;apply-exit" % bladename
                self.click(loc)
        self._wait_loading()

        # cancel
        self.try_click("//a[contains(@id,';cancel')]")

        # check if operation is SA and press apply:
        self.try_click("confirmAlert;apply")

        # check compld code
        response = self._check_status()
        self.try_click("//span[@title='Press ESC to close']")
        if response:
            raise RuntimeError(
                "Not possible to set parameter %s on %s" %
                (key, aid))
        # except Exception as ex:
            # if not self.try_click("//span[@title='Press ESC to close']"):
            # self.try_click("//a[contains(@id,';cancel')]")
            # raise ex

    def set_crypto_param(self, aid, crypto_pw, key, value):
        """Set crypto params on ARE modules."""
        try:
            aidtype = aid.split('-')[0]

            if key == "AUTHPW":
                # detail window of network channel entity
                self.seek_parameter(aid, 'ALIAS')
                self.try_click("_wizard;set-auth-key")
                self._crypto_officer_change(crypto_pw)
                self.set_value('crypto', 'current-password', crypto_pw)
                self.set_value('crypto', 'new-authkey', value)
                self.set_value('crypto', 'confirm-authkey', value)
                self.try_click("_crypto;changeAuthKey;apply")
                self.try_click("//span[@title='Press ESC to close']")
            elif key == "CRYPW":
                # Change crypto off passwd in Maintain on module
                self.seek_parameter(aid, 'CRY-RESET')
                self.try_click("_crypto;password-reset")
                self._crypto_officer_change(crypto_pw, value)
            else:
                # find parameter location
                applname, blade = self.seek_parameter(aid, key, edit=True)
                bladename = re.sub(r'[^\w]', '', blade).lower()
                self._crypto_officer_change(crypto_pw)
                # change value to NED naming
                if (key, value) in self._jsdata.val2name:
                    value = self._jsdata.val2name[key, value]
                # set value of parameter
                if bladename == "portencryption":
                    if key in ["KEX-RESET", "KEYXCH__OPERATION"]:
                        loc = '__' + bladename + aid + ";" + key
                        self.click(loc)
                    else:
                        self.set_value('_' + bladename + aid, key, value)
                else:
                    self.set_value(aid, key, value)

                # Approve setting parameter
                if applname == 'Maintain':
                    loc = "_%s;apply" % bladename
                    self.click(loc)
                else:
                    loc = "_wizard;apply-exit"
                    if not self.try_click(loc):
                        if aidtype in ['MOD', 'SHELF']:
                            loc = "_simple;apply-exit"
                        else:
                            loc = "_%s;apply-exit" % bladename
                        self.click(loc)
                # check if crypto office password is needed:
                if "_crypto;current-password" in self:
                    self.set_value("crypto", "current-password", crypto_pw)
                    self.click('_crypto;passwordProvide;apply')
                self.try_click("//span[@title='Press ESC to close']")
            self._wait_loading()
        except Exception as ex:
            self.try_click("//span[@title='Press ESC to close']")
            raise ex

    def set_entity_param_crsch(self, aid, key, value):
        """Set entity."""
        # try:
        (aidfrom, aidto) = str(aid).split('CRS_CH-')[1].split(',')
        aidfromtype = aidfrom.split('-')[0]

        # going to the proper blade
        if aidfromtype in ['CH']:
            blade = self.seek_parameter(aidto, 'EP_AID')[1]
        else:
            blade = self.seek_parameter(aidfrom, 'EP_AID')[1]

        # FORCED ADMIN modification
        if blade is None and key == 'ADMIN':
            key = 'EP_ADMIN_FORCED'
            if aidfromtype in ['CH']:
                blade = self.seek_parameter(aidto, key)[1]
            else:
                blade = self.seek_parameter(aidfrom, key)[1]

        bladename = re.sub(r'[^\w]', '', blade).lower()
        # change value to NED naming
        if (key, value) in self._jsdata.val2name:
            value = self._jsdata.val2name[key, value]

        # opening detail window of CRS
        loc = "//td[span[@id[contains(.,'_%s')]]]" % aid
        self.click(loc)
        self._wait_loading()

        if value == self.get_value(aid, key):
            self.try_click("//span[@title='Press ESC to close']")
            self.try_click("//a[contains(@id,';cancel')]")
            return

        # ID can be aid or return aid
        return_aid = "CRS_CH-%s,%s" % (aidto, aidfrom)

        # set value of parameter
        for loc_aid in [aid, return_aid]:
            try:
                self.set_value(loc_aid, key, value)
                break
            except Exception:
                if key == 'ADMIN':
                    self.set_value(aid, 'EP_ADMIN_FORCED', value)
                    break
        else:
            raise Exception

        # Approve setting parameter
        loc = "_wizard;apply-exit"
        if not self.try_click(loc):
            loc = "_%s;apply-exit" % bladename
            self.click(loc)
        self._wait_loading()

        # cancel
        self.try_click("//a[contains(@id,';cancel')]")

        # check if operation is SA and press apply:
        self.try_click("confirmAlert;apply")

        # check compld code
        response = self._check_status()
        self.try_click("//span[@title='Press ESC to close']")
        if response:
            raise RuntimeError(
                "Not possible to set parameter %s on %s" %
                (key, aid))
        # except Exception as ex:
            # if not self.try_click("//span[@title='Press ESC to close']"):
            # self.try_click("//a[contains(@id,';cancel')]")
            # raise ex

    def set_entity_eqpt(self, aid, param, value):
        """Set entity on EQPT - update FWP or reboot."""
        # try:

        shelf, module = None, None
        aidtype = aid.split('-')[0]
        if len(aid.split('-')) >= 2:
            shelf = aid.split('-')[1]
        if len(aid.split('-')) >= 3:
            module = aid.split('-')[2]

        if value == "REBOOT":
            # find parameter location
            self.change_appl('Maintain')

            # moving to the module in maintian apllication
            loc = "//span[../span/span[@id='_SHELF-%s;tree'] " % shelf + \
                "and contains(.,'+')]"
            if loc in self:
                self.click("//img[../span/span[@id='_SHELF-%s;tree']]" %
                           shelf)
            # read Shelf type
            if module == 'FCU' or aidtype == 'FCU':
                loc = "//span[@id='_FCU-%s;tree']/span" % shelf
            else:
                loc = "//span[@id='_MOD-%s-%s;tree']/span" % (shelf, module)
            if loc in self:
                if aidtype not in ['SHELF']:
                    self.click(loc)
            # set value of parameter
            # open restart window
            self.set_value(aid, 'EP_COMMAND__EQPT_REBOOT', value)
            # choose restart type
            saff = 'NSA'
            if 'SA' in self._srvubr:
                saff = self._srvubr['SA']
            self.click('radio%s' % saff)
            self._wait_loading()
            # approve module restart
            self.click(
                '_modulerestartdialog;restart-mod-%s-%s;restart' %
                (shelf, module))
        else:
            # going to the proper blade
            self.seek_parameter('EQPT-UBR-%s' % aid, param)

            # single FWP update
            if aid != "NE":
                # open details
                loc = "//tr[td[text()='%s']]" % aid
                self.click(loc)
            else:
                # multi FWP update
                # change to Type:
                loc = "//*[contains(@id,'_software;module;type')]" + \
                    "//span[.='Type']"
                self.click(loc)
            self._wait_loading()
            # change NED name to YP
            if (param, value) in self._jsdata.val2name:
                value = self._jsdata.val2name[param, value]
            value = value.replace(' ', '').lower()
            # choose proper action
            loc = "//*[substring(@id, string-length(@id) - " + \
                "string-length('%s')+1) = '%s']" % (value, value)
            self.click(loc)
            time.sleep(5)
            # wait until process ends
            loc = "//span[contains(@id,'refresh') and " + \
                "@role='button' and @aria-disabled='true']"
            self._wait_loading(loc)

        # check compld code
        response = self._check_status()
        if response:
            raise RuntimeError(
                "Not possible to set parameter %s on %s" %
                (param, aid))
        # except Exception as ex:
            # if not self.try_click("//span[@title='Press ESC to close']"):
            # self.try_click("//a[contains(@id,';cancel')]")
            # raise ex

    def multiset_srv(self, aid, keys_and_values):
        """Set parameters from keys_and_values and key.

        Placed in one location in the NED interface
        """
        # try:
        param, value = None, None
        # finding parameter location
        if 'COMMAND__NCU' in keys_and_values:
            param = 'COMMAND__NCU'
            value = keys_and_values[param]
            keys_and_values.pop(param)
        elif 'COMMAND__EQPT' in keys_and_values:
            param = 'COMMAND__EQPT'
            value = keys_and_values[param]
            keys_and_values.pop(param)

        if param == 'COMMAND__NCU' and value == 'AUTO_DOWNLOAD_AND_INSTALL':
            self.seek_parameter(aid, param, value)
            self._wait_loading("//*[contains(@id,'_software']")
            # old id for FILE:
            if self._gissue < 15:
                self.set_value(
                    'software;ncu;transfersoftwaretostandbyarea',
                    'FILE',
                    keys_and_values['FILE'])
                keys_and_values.pop('FILE')
            else:
                # FILE can be set in parame queue
                pass
            if 'IP' in keys_and_values:
                keys_and_values['IPV4V6'] = keys_and_values['IP']
                keys_and_values.pop('IP')
            # parameter queue
            self.param_queue(aid, keys_and_values)
            if self._gissue < 15:
                self.set_value(
                    'software;ncu;standbysoftwareupdate', 'update', "")
            else:
                self.set_value(
                    'software;ncu;transfersoftwaretostandbyarea', 'start', "")

            time.sleep(10)
            self._wait_loading()
        elif param == 'COMMAND__NCU' and value in ['ACTIVATE',
                                                   'ACTIVATE_WITH_FWP']:
            self.seek_parameter(aid, param, value)
            self._wait_loading("//*[contains(@id,'_software']")
            self._wait_loading(
                "//*[contains(@id," +
                "'software;ncu;activatesoftwareinstandbyarea']")
            if self._gissue < 15:
                self.set_value(
                    'software;ncu;transfersoftwaretostandbyarea',
                    'activate',
                    "")
            else:
                self.set_value(
                    'software;ncu;activatesoftwareinstandbyarea',
                    'activate',
                    "")

            self._wait_loading()
            # choose dbs behavior
            loc = "//input[@value='%s' and @type='radio']" % \
                keys_and_values['DBSRST']
            self.click(loc)
            # more params to set if FWP upgrade during activation is performed
            if value == 'ACTIVATE_WITH_FWP':
                self.click(
                    "//*[@id='_software;ncu;" +
                    "activationofsoftwareinstandbyarea;activatefwponmodules']")
                if keys_and_values['SA'] != 'NSA':
                    sa = self._jsdata.val2name['SA', keys_and_values['SA']]
                    self.set_value('SRV-UBR', 'SA', sa)
                if keys_and_values['TYPE__EQPT'] != '__UNKNOWN':
                    self.set_value(
                        'SRV-UBR',
                        'TYPE__EQPT',
                        keys_and_values['TYPE__EQPT'])

            # apply
            self.set_value(
                'software;ncu;activationofsoftwareinstandbyarea',
                'apply',
                "")
            time.sleep(10)
            self._wait_loading()
        elif param == 'COMMAND__NCU' and value == 'REBOOT':
            self.change_appl('Overview')
            loc = "//span[.='Management Network']"
            self.click(loc)
            self._wait_loading()
            # NCU restrat button
            loc = "//*[@id='_management-network;ncurestart']"
            self.click(loc)
            self._wait_loading()
            # confirm NCU reboot
            loc = "//*[@id='_management-network;confirmncurestart;restart']"
            self.click(loc)
            time.sleep(10)
        elif param == 'COMMAND__NCU' and '_ALP' in value:
            self.seek_parameter(aid, param, value)
            # show proper blade
            if value == 'IMPORT_ALP':
                bld = 'profiles;alarm;importasstandbyprofile'
                self.try_click(
                    "//div[@id='_%s' " % bld +
                    "and div[contains(@class,'dijitClosed')]]/div")
                # change destination to rdisk
                self.set_value(bld, 'sourceloaction', 'Active NCU RAM')
                # click proper button
                self.set_value(bld, 'import', '')
            elif value == 'EXPORT_ALP':
                bld = 'profiles;alarm;exportactiveprofile'
                self.try_click(
                    "//div[@id='_%s' " % bld +
                    "and div[contains(@class,'dijitClosed')]]/div")
                # change destination to rdisk
                self.set_value(bld, 'destination', 'Active NCU RAM')
                # click proper button
                self.set_value(bld, 'export', '')
            elif value == 'ACTIVATE_ALP':
                # click proper button
                self.set_value('profiles;alarm;standbyprofile',
                               'activate', '')
            elif value == 'ACTIVATE_FD_ALP':
                self.set_value(
                    'profiles;alarm;activeprofile',
                    'clearallchanges',
                    '')
                # approve rtf
                self.set_value(
                    'profiles;alarm;clearallchanges',
                    'clearallchanges',
                    '')
            self._wait_loading()
        # check compld code
        response = self._check_status()
        if response:
            raise RuntimeError(
                "Not possible to set parameter %s on %s" %
                (param, aid))
        return True
        # except Exception as ex:
        # if not self.try_click("//span[@title='Press ESC to close']"):
        # self.try_click("//a[contains(@id,';cancel')]")
        # raise ex

    def multiset_copy(self, aid, keys_and_values):
        """Set parameters from keys_and_values and key.

        Placed in one location in the NED interface
        """
        # try:
        param, value = None, None

        # finding parameter location
        if 'COMMAND__COPY' in keys_and_values:
            param = 'COMMAND__COPY'
            value = keys_and_values[param]
            keys_and_values.pop(param)

        self.seek_parameter(aid, param, value)
        if param == 'COMMAND__COPY' and value == 'DOWNLOAD':
            # click on Download button
            self.click('_file-storage;download')
            self._wait_loading()
            if 'IP' in keys_and_values:
                keys_and_values['IPV4V6'] = keys_and_values['IP']
                keys_and_values.pop('IP')
            # parameter queue
            self.param_queue(aid, keys_and_values)
            # confirm download
            self.click('_file-storage;downloadfile;download')
            self._wait_loading()
        elif param == 'COMMAND__COPY' and value == 'UPLOAD':
            # click on proper filename
            self.click("//*[.='%s']" % keys_and_values['FILE'])
            self._wait_loading()
            if 'IP' in keys_and_values:
                keys_and_values['IPV4V6'] = keys_and_values['IP']
                keys_and_values.pop('IP')
            # parameter queue
            self.param_queue(aid, keys_and_values)
            # confirm download
            self.click('_file-storage;downloadfile;download')
            self._wait_loading()
        # check compld code
        response = self._check_status()
        if response:
            raise RuntimeError(
                "Not possible to set parameter %s on %s" %
                (param, aid))
        return True
        # except Exception as ex:
        # if not self.try_click("//span[@title='Press ESC to close']"):
        # self.try_click("//a[contains(@id,';cancel')]")
        # raise ex

    # TODO
    # def set_entity_remauth(self, aid, key_and_value):
    # def set_entity_ne(self, aid, key_and_value):
    # def set_entity_passiveshelf(self, aid, key_and_value):

    # ============================
    # Gathering PMs Methods
    # ============================

    def get_current_pm(self, aid, param, group):
        """Return current PM record."""
        # gathering current PM
        try:
            record = {}
            # set time group
            param_seek, group = self._change_time_period(param, group)
            # finding parameter
            self.seek_parameter(aid, param_seek)
            self._wait_loading()
            # get PM value
            if param in ['OPR', 'OPT', 'OSCOPT', 'OSCPWR']:
                for key in [param + suf for suf in ['-L', '-M', '-H']]:
                    record[key] = self.str2num(self.get_value(aid, key))
            elif '__COUNTER' in param:
                record['VALID'] = False
                # all cells in the row
                loc = "//tr[td/span[@id='_%s;EP_AID']]/td/span" % aid
                cells = self.driver.find_elements_by_xpath(loc)
                for cell in cells:
                    # get name of the parameter in cell
                    name = cell.get_attribute('id').split(';')[1]
                    # drop all EP parameters
                    if 'EP_' not in name:
                        record[str(name)] = self.str2num(cell.text)
            else:
                record[param] = self.str2num(self.get_value(aid, param))
            # get elapsed time
            try:
                record['ELAPSED'] = self._elapsed_time(aid, group)
            except Exception:
                pass  # there is no elapsed time for this param

            # change VALID from string to boolean type
            record["VALID"] = False

            return record
        except Exception as ex:
            raise ex

    def get_pm_records(self, aid, param, group, amount):
        """Return given amount of PM records."""
        # gathering historical PMs
        try:
            records = []
            record = {}
            # set time group
            param_seek, group = self._change_time_period(param, group)
            # finding parameter
            self.seek_parameter(aid, param_seek, history=True)
            self._wait_loading()
            for i in range(1, amount + 1):
                record['VALID'] = True
                timeid = "_%s;%s;%s;timestampDisp" % (i, aid, group)
                record['TIMESTAMP'] = str(self.get_value_loc(timeid)) + ".00"
                if param in ['OPR', 'OPT', 'OSCOPT', 'OSCPWR']:
                    for key in [param + suf for suf in ['-L', '-M', '-H']]:
                        loc = "//tr[td/span[@id='%s']]//span[@id='_%s;%s']" % (
                            timeid, i, key)
                        record[key] = self.get_value_loc(loc)
                        if record[key].find('*') > 0:
                            record['VALID'] = False
                            record[key] = record[key].replace('*', '')
                        record[key] = self.str2num(record[key])
                elif '__COUNTER' in param:
                    # iteration on whole row
                    # all cells in the row
                    loc = "//tr[td/span[@id='%s']]/td/span" % timeid

                    cells = self.driver.find_elements_by_xpath(loc)
                    for cell in cells:
                        # get name of the parameter in cell
                        name = cell.get_attribute('id').split(';')[-1]
                        key = str(name)
                        if key == 'timestampDisp':
                            record['TIMESTAMP'] = str(cell.text) + ".00"
                        # drop all EP parameters
                        elif 'EP_' not in key:
                            record[key] = cell.text
                            if record[key].find('*') > 0:
                                record['VALID'] = False
                                record[key] = record[key].replace('*', '')
                            record[key] = self.str2num(record[key])
                else:
                    loc = "//tr[td/span[@id='%s']]//span[@id='_%s;%s']" % (
                        timeid, i, param)
                    record[param] = self.get_value_loc(loc)
                    if record[param].find('*') > 0:
                        record['VALID'] = False
                        record[param] = record[param].replace('*', '')
                    record[param] = self.str2num(record[param])
                records.append(record)
            return records
        except Exception as ex:
            raise ex
    # ============================
    # Gathering Events Methods
    # ============================

    def getlasteventnumber(self):
        """Return counter of the last event arraved at the system."""
        self.seek_parameter('LOG', 'Event')
        self._wait_loading()

        # cell location
        cellx = "//div[@id='eventLogGrid']//div[@class='dojoxGridContent']" + \
            "/div/div[1]//td[1]"
        stevent = self.get_value_loc(cellx)

        # check if next record has lower value
        cellx = "//div[@id='eventLogGrid']" + \
            "//div[@class='dojoxGridContent']/div/div[2]//td[1]"
        ndevent = self.get_value_loc(cellx)
        if int(ndevent) < int(stevent):
            return stevent
        else:
            return ndevent

    def geteventlog(self, start_marker, quantity):
        """Return quantity amount of eventlogs, starting from start_marker."""
        records = []
        start_number = False
        self.seek_parameter('LOG', 'Event')

        self._wait_loading()
        rown = 1
        while not start_number:
            record = {}
            rowx = self[
                "//div[@id='eventLogGrid']//div[@class='dojoxGridContent']" +
                "/div/div[%s]//tr" % rown
            ]
            # Event number
            record['EVENTNUMBER'] = rowx.find_element_by_xpath(".//td[1]").text
            if record['EVENTNUMBER'] == start_marker:
                start_number = True
            # timestamp
            record['DATE'] = rowx.find_element_by_xpath(".//td[2]").text
            # AID
            record['AID'] = rowx.find_element_by_xpath(".//td[3]").text
            # description (in YP naming)
            cond = rowx.find_element_by_xpath(".//td[4]").text
            record['CONDITION'] = self._jsdata.name2param[cond]
            # Severity
            record['CURR-SEVERITY'] = self.severity_trans(
                rowx.find_element_by_xpath(".//td[5]").text)
            # Status
            status = rowx.find_element_by_xpath("//td[6]").text
            if status == 'SET':
                record['CURR-STATUS'] = 'SET'
            else:
                record['CURR-STATUS'] = 'CLEAR'
            # add record to the list
            records.append(record)
            rown += 1

        # get proper quantity of entries:
        return records[-int(quantity) - 1:-1]

    # ============================
    # Gathering Secondary states method
    # ============================

    def get_entity_secondary_states(self, aid):
        """Return list of secondary states."""
        states_list = []
        # UEQ secondary state occurs on all entities in js file
        self.seek_parameter(aid, 'UEQ')
        # locator for visible secondary states
        paneid = 'secondarystates'
        label = 'No secondary states'
        loc = "//li[@titlepaneid='%s' and not" % paneid + \
              "(@style='display: none;')" + \
            " and not(div[label='%s'])]" % label
        elements = self.driver.find_elements_by_xpath(loc)

        if len(elements) != 0:
            # get secondary state's name
            for elem in elements:
                states_list.append(elem.get_attribute('id')[3:])

        # close detail window if needed
        self.try_click("//span[@title='Press ESC to close']")

        return states_list

    # ============================
    # Gathering Conditions Method
    # ============================

    def get_entity_conditions(self, aid):
        """Return list of conditions."""
        cond_dict = {}
        shelf, module, typeeqpt = None, None, None
        aidtype = aid.split('-')[0]
        if len(aid.split('-')) >= 2:
            shelf = aid.split('-')[1]
        if len(aid.split('-')) >= 3:
            module = aid.split('-')[2]

        # go to the proper f7module in alarm tree
        self.change_appl('Alarm')

        # moving to the module to filer alarms
        if aidtype in ['ECH']:
            self.click("_ECI;tree")
        elif aidtype in ['PSH']:
            self.click("_PSHS;tree")
        else:
            loc = "//span[../span/span[@id='_SHELF-%s;tree'] " % shelf + \
                "and contains(.,'+')]"
            if loc in self:
                self.click("//img[../span/span[@id='_SHELF-%s;tree']]" % shelf)
            # read Shelf type
            loc = "//*[@id='_SHELF-%s;tree']/span" % shelf
            if loc in self:
                self.click(loc)
                typeeqpt = self.get_value_loc(loc)
                typeeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', typeeqpt]
            if (module and typeeqpt not in ['EROADM-DC']) or aidtype == 'FCU':
                if module == 'FCU' or aidtype == 'FCU':
                    loc = "//span[@id='_FCU-%s;tree']/span" % shelf
                else:
                    loc = "//span[@id='_MOD-%s-%s;tree']/span" % (
                        shelf, module)
                if loc in self:
                    if aidtype not in ['SHELF']:
                        self.click(loc)
        self._wait_loading()
        # change to reported alarm
        loc = "//div[label[.='Alarm Severity ']]/table"
        tabid = self[loc].get_attribute('id')
        loc = "//table[@id='%s']" % tabid
        self.click(loc)
        loc = "//div[@id='%s_menu']/table/tbody/tr[td='Reported']" % tabid
        self.click(loc)
        self._wait_loading()
        # set id of alarms grid
        if self._gissue > 15.011:
            grid_id = 'alarms'
        else:
            grid_id = 'alarmsBigGrid'
        # iterate on all rows
        rown = 0
        while True:
            rowx = "//div[@id='%s']//div[@class='dojoxGridContent']//tr" % \
                grid_id
            try:
                row = self.driver.find_elements_by_xpath(rowx)[rown]
            except Exception:
                break
            row.location_once_scrolled_into_view
            if str(row.find_element_by_xpath("td[3]").text) == aid:
                severity = self.severity_trans(
                    row.find_element_by_xpath("td[5]").text)
                timestamp = row.find_element_by_xpath(
                    "td[2]").text.split('.')[0]
                alarm = self._jsdata.name2param[
                    row.find_element_by_xpath("td[4]").text]
                sa = self.sa_trans(row.find_element_by_xpath("td[7]").text)
                cond_dict[alarm] = [severity, sa, timestamp]
            rown += 1
        # change to not reported alarm
        loc = "//div[label[.='Alarm Severity ']]/table"
        tabid = self[loc].get_attribute('id')
        loc = "//table[@id='%s']" % tabid
        self.click(loc)
        loc = "//div[@id='%s_menu']/table/tbody/tr[td='Not Reported']" % tabid
        self.click(loc)
        self._wait_loading()
        # iterate on all rows
        rown = 0
        while True:
            rowx = "//div[@id='%s']//div[@class='dojoxGridContent']//tr" % \
                grid_id
            try:
                row = self.driver.find_elements_by_xpath(rowx)[rown]
            except Exception:
                break
            row.location_once_scrolled_into_view
            if str(row.find_element_by_xpath("td[3]").text) == aid:
                severity = self.severity_trans(
                    row.find_element_by_xpath("td[5]").text)
                timestamp = row.find_element_by_xpath(
                    "td[2]").text.split('.')[0]
                alarm = self._jsdata.name2param[
                    row.find_element_by_xpath("td[4]").text]
                cond_dict[alarm] = [severity, timestamp]
            rown += 1
        return cond_dict

    # ============================
    # User Section
    # ============================
    def create_user(self, user, **keys_and_values):
        """Create entity."""
        pref = ''
        # go to the User management
        self.change_appl('Node')
        self.try_click("//div[span[span='Users'] and contains(.,'+')]")

        if self._gissue > 13.02:
            self.click("//span[span='Manage']")
            pref = ';manage'
        # open wizard
        self.click("//a[@id='_users%s;add']" % pref)

        # wait for wizard window
        self._wait_loading()

        # change to NED naming
        ned_dict = self._user_extended_params(keys_and_values)

        # add username and password confirmation
        ned_dict['EP_USER_NAME'] = user
        ned_dict['retypepassword'] = ned_dict['password']

        self.set_value('EA_UID-NONE', 'EP_PRIVILEGE', ned_dict['EP_PRIVILEGE'])
        ned_dict.pop('EP_PRIVILEGE')
        # access restrictions
        if any('ACCESS-' in par for par in ned_dict.keys()):
            # retrtication checkbox
            self.click("//input[@id='checkboxAccessDayTime' " +
                       "and not(@aria-pressed='true')]")
        # parameter queue (for ned user)
        self.param_queue('EA_UID-NONE', ned_dict)

        # add and check
        self.click("_users%s;addaccount;add" % pref)

        self._wait_loading()
        # check compld code
        response = self._check_status()
        self.try_click("//span[@title='Press ESC to close']")
        if response:
            raise RuntimeError(
                "Not possible to create %s: %s" %
                (user, response))

    def get_user_param(self, user, param):
        """Get user parameter."""
        # go to the User management
        self.change_appl('Node')
        self.try_click("//div[span[span='Users'] and contains(.,'+')]")

        if self._gissue > 13.02:
            self.click("//span[span='Manage']")

        # wait for user list
        self._wait_loading()

        # change to NED naming
        param = self._user_extended_params(param)

        # check if parameter is already shown
        loc = "//td[contains(@id,'EA_UID-%s;%s')]" % (user, param)
        if loc in self:
            value = self.get_value_loc(loc)
        else:
            # open user details
            loc = "//td[contains(@id,'EA_UID-%s;EP_USER_NAME')]" % user
            self.click(loc)
            self._wait_loading()
            value = self.get_value('EA_UID-%s' % user, param)

        # change NED name to YP
        if (param, value) in self._jsdata.name2val:
            value = self._jsdata.name2val[param, value]

        # check compld code
        response = self._check_status()
        self.try_click("//span[@title='Press ESC to close']")
        if response:
            raise RuntimeError(
                "Not possible to create %s: %s" %
                (user, response))
        return value

    def set_user_param(self, user, key, value):
        """Set user parameter."""
        pref = ''
        # go to the User management
        self.change_appl('Node')
        self.try_click("//div[span[span='Users'] and contains(.,'+')]")

        if self._gissue > 13.02:
            self.click("//span[span='Manage']")
            pref = ';manage'

        # wait for user list
        self._wait_loading()

        # change to NED naming
        ep_dict = self._user_extended_params({key: value})
        param, value = ep_dict.items()[0]
        # open user details
        loc = "//td[contains(@id,'EA_UID-%s;EP_USER_NAME')]" % user
        self.click(loc)
        self._wait_loading()
        self.set_value('EA_UID-%s' % user, param, value)

        # retype password if needed
        if param == 'newpassword':
            self.set_value('EA_UID-%s' % user, 'confirmnewpassword', value)

        # approve changes
        self.click("_users%s;editaccount;apply" % pref)

        self._wait_loading()
        # check compld code
        response = self._check_status()
        self.try_click("//span[@title='Press ESC to close']")
        if response:
            raise RuntimeError(
                "Not possible to set %s on %s: %s" %
                (key, user, response))

    def destroy_user(self, user):
        """Destroy given user from user table."""
        pref = ''
        # go to the User management
        self.change_appl('Node')
        self.try_click("//div[span[span='Users'] and contains(.,'+')]")
        if self._gissue > 13.02:
            self.click("//span[span='Manage']")
            pref = ';manage'
        self._wait_loading()
        # open user details
        loc = "//td[contains(@id,'EA_UID-%s;EP_USER_NAME')]" % user
        self.click(loc)

        # wait for deatils window
        self._wait_loading()

        # delete and confirm
        self.click("_users%s;editaccount;deleteuser" % pref)
        self._wait_loading()
        self.click("_users%s;deleteaccount;ok" % pref)
        self._wait_loading()
        # check compld code
        response = self._check_status()
        self.try_click("//span[@title='Press ESC to close']")
        if response:
            raise RuntimeError(
                "Not possible to delete %s: %s" %
                (user, response))
