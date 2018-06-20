"""
NEDdriver based on selenium package provide functions to interact with
NED interface on the F7 system.
"""

import time
import re
from .jsimport import Jsdata
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from .version import version as __version__  # noqa: F401


class NEDdriver(object):
    """ NED driver class
    """
    def __init__(self):

        self._browser = {}
        self.driver = None
        self._ip_address = None
        self._server_ip = None      # address of external server
        self._alias = None
        self._session_expired = False
        self._jsdata = None
        self._gissue = None
        # UBR variables (have to be set at once in NED)
        self._srvubr = {}
        self._copyubr = {}

    def __getitem__(self, locator):
        """ Return existing element
        """
        try:
            time.sleep(0.1) # FIX ME - webbrowser is too slow
            # is element present:
            if locator.startswith('/') or locator.startswith('(/'):
                by_type = By.XPATH
            else:
                by_type = By.ID
            self.driver.implicitly_wait(0)
            elements = self.driver.find_elements(by_type, locator)
            self.driver.implicitly_wait(0.1)
            if elements:
                elem = elements[0]
                elem.location_once_scrolled_into_view
                return elem
            else:
                raise NoSuchElementException(locator)
        except StaleElementReferenceException:
            return self[locator]
        except:
            raise

    def __contains__(self, locator):
        """ Check if xpath is loaded
        """
        try:
            self[locator]
            return True
        except NoSuchElementException:
            return False

    # click with StaleElement exception handling
    def click(self, locator):
        """ Click on element and handle
            StaleElementReferenceException
        """
        try:
            if self[locator].get_attribute('aria-disabled') == 'true':
                raise
            else:
                self[locator].click()
        except StaleElementReferenceException:
            self[locator].click()
        except:
            raise NoSuchElementException("Not possible to click element %s" % locator)

    def try_click(self, locator):
        """ Try to click element
        """
        try:
            self.click(locator)
            return True
        except:
            return False

    def _wait_loading(self, loc=''):
        """Wait until loading finished
        """
        timeout = 200
        if loc == '':
            while "//*[contains(@class,'loading') and @class!='init-loading']" in self\
                  or "//*[@class!='init-loading']img[contains(@src,'/images/loadingAnimation.gif')]" in self\
                  or timeout == 0:
                self.driver.implicitly_wait(1)
                timeout -= 1
        else:
            while loc not in self or timeout == 0:
                self.driver.implicitly_wait(1)
                timeout -= 1

    def _check_status(self):
        """Check status of last operation from top message
        """
        try:
            loc = "//div[@id='topMessageBox']"
            if self[loc].get_attribute('class') == 'message error':
                return self["//div[@id='topMessageSpan']"].text
            return
        except NoSuchElementException:
            return

    def _eqpt_to_variant(self, params):
        """Translate TYPE__EQUIPMENT and set of parametrs
           to EQPT-VARIANT in NED interface
        """
        typeeqpt = ""
        eqpt_var = ""
        try:
            typeeqpt = params['TYPE__EQUIPMENT']
            if typeeqpt in self._jsdata.eqpt_variants:
                for var, pars in self._jsdata.eqpt_variants[typeeqpt].items():
                    for par, value in pars.items():
                        if params[par] != value:
                            break
                    else:
                        eqpt_var = var
                        break
            if eqpt_var == "":
                return typeeqpt
            else:
                return eqpt_var
        except:
            if typeeqpt in self._jsdata.eqpt_variants:
                return self._jsdata.eqpt_variants[typeeqpt].keys()[0]
            else:
                return typeeqpt

    def _get_gissue(self):
        loc = "//div[@id='HEADER;EP_GISSUE']"
        loc1 = "//div[@id='gissue']"
        if loc in self:
            gissue = self.get_value_loc(loc).split(' ')[1][:7].split('.')
        elif loc1 in self:
            gissue = self.get_value_loc(loc1).split(' ')[1][:7].split('.')
        else:
            # missing  header - set deafult
            gissue = '15.011'
            self._gissue = gissue
            return gissue
        rel = re.sub(r"\D", "", gissue[0])
        major = re.sub(r"\D", "", gissue[1])
        minor = re.sub(r"\D", "", gissue[2])
        gissue = float(rel + "." + major + minor)
        self._gissue = gissue
        return gissue

    def open_connection(self, ip_address, **kwargs):
        """Opens a NED connection
        if server_ip is passed in args - connect to remote selenium server
        """
        self._ip_address = ip_address
        if 'alias' in kwargs:
            self._alias = kwargs['alias']
        if 'server_ip' in kwargs:
            server_ip = kwargs['server_ip']
        else:
            server_ip = ''

        # browser type set to firefox
        if 'browser' in kwargs:
            self._browser = kwargs['browser']
        else:
            self._browser = 'firefox'

        if server_ip != '':
            self.driver = webdriver.Remote(
                desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
                command_executor='http://%s:4444/wd/hub' % server_ip
            )
        else:
            if self._browser == 'firefox':
                self.driver = webdriver.Firefox()
            else:
                raise RuntimeError('%s is not supported yet' % self._browser)
        try:
            self.driver.set_page_load_timeout(20)  # wait for page to load for 20 sec
            self.driver.get('http://%s' % ip_address)

        except TimeoutException:
            self.driver.close()
            raise RuntimeError('Not possible to open login page')

    def reopen_connection(self):
        """ Reopen connection if session expired
        """
        # query =  "//div[@id='errormsg' and contains(.,'Please log in again.')]"
        try:
            if 'user' in self:
                self.ned_login()
        except NoSuchElementException:
            pass

    def ned_login(self, user='ADMIN', password='CHGME.1a'):
        """Login to NED using user and password
        """
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "user")))
            self['user'].send_keys('%s' % user)
            self['password'].send_keys('%s' % password)
            self.click('blogin')
            script = "return webgui.application.hasOwnProperty('wizard')"
            timeout = 0
            response = ''
            while timeout < 180:
                timeout += 1
                try:
                    response = self.driver.execute_script(script)
                except:
                    pass
                if response:
                    break
            self._wait_loading()
            gis = repr(self._get_gissue()).split('.')
            if int(gis[1][:1]) == 0:
                gissue = 'R%s.%s.%s' % (gis[0], repr(int(gis[1][:2])), gis[1][-1:])
            else:
                gissue = 'R%s.%s.%s' % (gis[0], repr(int(gis[1][:1])), gis[1][-1:])
            # remove unneessary zero from the gissue
            self._jsdata = Jsdata(gissue)
        except NoSuchElementException:
            raise RuntimeError('Not possible to login')

    def ned_logout(self):
        """Logout from NED
        """
        try:
            self.click("//a[.='Logout']")
        except NoSuchElementException:
            raise RuntimeError('Not possible to logout')

    def close_connection(self):
        """Closing NED connection
        """
        # Logout to avoid open session
        try:
            self.click('Logout')
        except NoSuchElementException:
            pass

        # Close webbrowser
        self.driver.close()

    def change_appl(self, appl):
        """ Change NED application
        """
        qer = "//span[@aria-selected='false' and span[text()='%s']]" % appl
        try:
            self.click(qer)
        except NoSuchElementException:
            pass

        # waiting for loading tree (not in Overview and Node)
        if appl not in ['Overview', 'Node']:
            # FIX ME: change to WebDriverWait
            script = "return window.webgui.treeLoaded"
            timeout = 0
            while timeout < 180:
                response = self.driver.execute_script(script)
                timeout += 1
                if response:
                    break
        self.driver.implicitly_wait(2)

    def get_value_loc(self, locator):
        """Get value from locator. Depends on tag_name
        proper attribute is returned
        """
        try:
            elem = self[locator]
            if elem.tag_name in ['input', 'textarea']:
                return elem.get_attribute('value')
            elif elem.tag_name in ['span', 'table', 'div', 'td']:
                return elem.text
        except StaleElementReferenceException:
            # element refreshed
            return self.get_value_loc(locator)
        except:
            raise NoSuchElementException

    def get_value(self, aid, param):
        """Get value for aid and param (if
        """
        try:
            idname = "_%s;%s" % (aid, param)
            loc = "//*[@id='%s']" % idname
            if loc not in self:
                loc = "//*[substring(@id, string-length(@id) - string-length('%s')+1) = '%s']" %(idname, idname)
                if loc not in self:
                    loc = "//*[contains(@id,'%s')]" % idname
            return self.get_value_loc(loc)
        except:
            raise

    def set_value(self, aid, param, value=''):
        """Set parameter value . Depends on type of element
        proper behavior is used.
        REQ: Value in NED naming
        """
        try:
            # set directly to element or construct idname
            if param != "":
                idname = "_%s;%s" % (aid, param)
            else:
                idname = aid
            # Check if value is already set
            if value == self.get_value(aid, param):
                loc = "//*[@id='%s']" % idname
                if loc not in self:
                    loc = "//*[substring(@id, string-length(@id) - string-length('%s')+1) = '%s']" %(idname, idname)
                    if loc not in self:
                        loc = "//*[contains(@id,'%s')]" % idname
                elem = self[loc]
                if elem.get_attribute('role') not in ['button']:
                    return True

            # get element by id (span are not editable)
            loc = "//*[@id='%s']" % idname
            if loc not in self:
                loc = "//*[substring(@id, string-length(@id) - string-length('%s')+1) = '%s']" %(idname, idname)
                if loc not in self:
                    loc = "//*[contains(@id,'%s')]" % idname
            elem = self[loc]
            # if element is disabled
            if elem.get_attribute('aria-disabled') == 'true':
                if elem.get_attribute('aria-valuetext') == value:
                    # value is properly set
                    return True
                else:
                    raise
            if elem.tag_name in ['input'] and \
                    elem.get_attribute('type') in ['text', 'password']:
                # normal input
                elem.clear()
                elem.send_keys('%s' % value)
                # different handling for TYPE__EQUIPMENT
                if param in ['TYPE__EQUIPMENT', 'EQPT-VARIANT']:
                    # self.click("//*[@id='%s_popup']" % idname)
                    loc = "//*[@id='%s_popup']" % idname
                    self._wait_loading(loc)
                    self.click(loc)
                self.click("//body")
                if elem.get_attribute('aria-invalid') == 'true':
                    raise
            elif elem.get_attribute('type') == 'checkbox':
                # change checkbox state
                if elem.get_attribute('aria-pressed') == 'false':
                    if value in [True, 'ENABLE', 'ENABLED']:
                        elem.click()
                else:
                    if value in [False, 'DISABLE', 'DISABLED']:
                        elem.click()
            elif elem.tag_name == 'textarea':
                elem.clear()
                elem.send_keys('%s' % value)
            elif elem.get_attribute('role') == 'button':
                # click on button
                elem.click()
            elif elem.get_attribute('type') == 'select-multiple':
                # deselect all possibilities
                loc = "//div[select[@id='%s']]//input[@aria-pressed='true']" % idname
                while loc in self:
                    self.click(loc)
                for selects in value.split('&'):
                    loc = "//div[select[@id='%s']]/div/div[div='%s']/div/input" % (idname, selects)
                    if loc in self:
                        elem = self[loc]
                        if elem.is_displayed() is False:
                            elem.click()
                        if elem.is_selected() is False:
                            elem.click()
                        # exception if element was partially visible:
                        elem = self[loc]
                        if elem.is_selected() is False:
                            elem.click()
            elif elem.tag_name == 'select':
                # select proper values
                for selects in value.split(','):
                    loc = "//div[select[contains(@id,'%s')]]/div/div[div='%s']/div/input" % (param, selects)
                    if loc in self:
                        self.click(loc)
            elif elem.tag_name in ['input'] and elem.get_attribute('type') == 'HEXV2_TEXT':
                # value can be: 0xVAL, 0XVAL, VAL, input have to be 0xVAL
                elem.clear()
                if value[0:2] in ['0x', '0X']:
                    elem.send_keys('%s' % value)
                else:
                    elem.send_keys('0x%s' % value)
            elif elem.tag_name == 'table':
                # dropdown list
                elem.click()
                try:
                    loc = "//div[contains(@id,'%s_menu')]/table/tbody/tr[td='%s']" % (idname, value)
                    self.click(loc)
                except NoSuchElementException:
                    loc = "//div[contains(@id,'%s_menu')]/table/tbody/tr/td[contains(.,'%s')]" % (idname, value)
                    self.click(loc)
            else:
                # element not recognized
                raise
            self._wait_loading()
            return True
        except StaleElementReferenceException:
            # element refreshes
            self.set_value(aid, param, value)
        except:
            raise Exception("Not possible to set %s of %s on %s" % (value, param, aid))

    def choose_slot(self, aid):
        """Choosing proper slot in wizard
        """
        try:
            shelf, module, port = '', '', ''
            aidtype = aid.split('-')[0]
            if len(aid.split('-')) >= 2:
                shelf = aid.split('-')[1]
            if len(aid.split('-')) >= 3:
                module = aid.split('-')[2]
            if len(aid.split('-')) >= 4:
                port = aid.split('-')[3]
            # check if preselect occurs
            loc = "//table[@id='_wizard;preselect']"
            if loc in self:
                if 'NE' in port:
                    port_select = 'NE'
                elif 'NW' in port:
                    port_select = 'NW'
                else:
                    port_select = port

                for key in ['CH', 'OM']:
                    script = "return window.webgui.wizard.aid2label['%s-%s-%s-%s']" \
                        % (key, shelf, module, port_select)
                    aidlabel = self.driver.execute_script(script)
                    if aidlabel is not None:
                        break
                else:
                    script = "return window.webgui.wizard.aid2label['OL-%s']" \
                        % shelf
                    aidlabel = self.driver.execute_script(script)
                    if aidtype == 'ECH':
                        script = "return window.webgui.wizard.aid2label['MOD-%s-%s']" \
                        % (shelf, module)
                        aidlabel = self.driver.execute_script(script)
                self.try_click("//table[@id='_wizard;preselect']")
                loc = "//div[@id='_wizard;preselect_menu']/table/tbody/tr[td='%s']" % aidlabel
                if loc in self:
                    ActionChains(self.driver).move_to_element(self[loc]).perform()
                    ActionChains(self.driver).move_to_element(self[loc]).click().perform()
                else:
                    self.try_click("//span[@title='Press ESC to close']")
                    raise RuntimeError('Not possible to choose slot for aid %s' % aid)
                self._wait_loading()
            # super channel entity:
            if aidtype in ['OWLG']:
                self.try_click("//input[@id='checkboxChannelGroup' and @aria-pressed='true']")
            # choose slot
            if "//input[@id='_wizard;slot']" in self:
                self.set_value('wizard', 'slot', aid)
            elif "//input[@id='inputServiceID']" in self:
                self.set_value('inputServiceID', '', module)
            else:
                self.try_click("//table[@id='_wizard;slot']")
                script = "return window.webgui.wizard.aid2label['%s']" % aid
                aidlabel = self.driver.execute_script(script)
                if aidlabel in ['null', None]:
                    if aidtype in ['PSH']:
                        loc = "//div[@id='_wizard;slot_menu']/table/tbody/tr[td='%s']" % aid[4:]
                    elif aidtype in ['OTLG']:
                        loc = "//div[@id='_wizard;slot_menu']/table/tbody/tr[td='%s']" % aid[5:]
                    else:
                        loc = "//div[@id='_wizard;slot_menu']/table/tbody/tr[td='%s']" % aid
                else:
                    loc = "//div[@id='_wizard;slot_menu']/table/tbody/tr[td='%s']" % aidlabel
                if loc in self:
                    ActionChains(self.driver).move_to_element(self[loc]).perform()
                    ActionChains(self.driver).move_to_element(self[loc]).click().perform()
                else:
                    self.try_click("//span[@title='Press ESC to close']")
                    raise Exception('Not possible to choose slot for aid %s' % aid)
        except NoSuchElementException:
            # clean up - close wizard window
            self.try_click("//span[@title='Press ESC to close']")
            raise Exception("Entity already assigned")

    def param_queue(self, aid, params):
        """ Setting parameters in wizard
        """
        self._wait_loading()
        # TYPE__EQUIPMENT/FACILITY has to be set as first step
        if 'TYPE__EQUIPMENT' in params:
            # setting TYPE__EQUIPMENT
            typeeqpt = self._jsdata.val2name['TYPE__EQUIPMENT', params['TYPE__EQUIPMENT']]
            try:
                self.set_value(aid, 'TYPE__EQUIPMENT', typeeqpt)
            except:
                self.set_value(aid, 'EQPT-VARIANT', typeeqpt)
            params.pop('TYPE__EQUIPMENT')
        elif 'TYPE__FACILITY' in params:
            # setting TYPE__FACILITY
            typefac = self._jsdata.val2name['TYPE__FACILITY', params['TYPE__FACILITY']]
            self.set_value(aid, 'TYPE__FACILITY', typefac)
            params.pop('TYPE__FACILITY')

        # show all blades:
        loc = "//div[@id='wizardMainPane']//div[not(@style='display: none;')]/div//div[img and span[contains(.,'+') ]]"
        while loc in self:
            self.click(loc)
        # queue
        queue = params.items()
        # number of iteration
        watchdog = len(queue) ** 2
        while queue:
            if watchdog == 0:
                break
            else:
                watchdog -= 1
            par, val = queue.pop(0)
            # change value to NED naming
            if (par, val) in self._jsdata.val2name:
                val = self._jsdata.val2name[par, val]

            # parameter is pre-set and is disabled
            # in this case, we remove this parameter from list and continue if it has the same
            # value as should be set
            # if this parameter has diffrent default value, it will be put at the end
            # of setting queue
            try:
                self.set_value(aid, par, val)
                self._wait_loading()
            except:
                # parameter is not settable yet
                # change back value to YP
                if (par, val) in self._jsdata.name2val:
                    val = self._jsdata.name2val[par, val]
                queue.append((par, val))

        if queue:
            raise RuntimeError("Not all parameters are set: %s on %s" % (queue, aid))

        self._wait_loading()

    def context_menu(self, aid, option):
        """Choosing option from context tree menu for specific aid
        """
        elem = self["//span[@id='_%s;tree']" % aid]
        ActionChains(self.driver).context_click(elem).perform()
        elem = self["//div/table/tbody/tr[td='%s']" % option]
        ActionChains(self.driver).click(elem).perform()
        return True

    # -------------------------------------------------------------------------------------

    def seek_parameter(self, aid, param, value=None, edit=False, history=False):
        """ Search dictionaries from js files to locate parameter for aid
            and find it in opened browser.
            If you want to edit this parameter set edit flag to True.
            If you want to search historical PMs set history flag to True.
            This will switch to edit mode iin NED.
        """
        aidtype, typeeqpt, shelf, module = None, None, None, None
        config_detail = False
        aidtype = aid.split('-')[0]
        if aidtype in ['CRS_FLW']:
            shelf = aid[8:].split('-')[1]
            module = aid[8:].split('-')[2]
        else:
            if len(aid.split('-')) >= 2:
                shelf = aid.split('-')[1]
            if len(aid.split('-')) >= 3:
                module = aid.split('-')[2]

        # Parameters from NODE application
        if aid in ['NE', 'TIME-NTP'] or 'NTPSRV-' in aid or 'REMAUTH' in aid \
           or 'LOG' in aid or 'UBR' in aid:
            applname, blade = self._seek_node(aid, param, value, edit)
            return applname, blade

        # Optical lines and dependent entities:
        if aidtype in ['OL', 'WCH', 'OWLG']:
            self.change_appl('Configure')
            self.click("_OLS;tree")
            typeeqpt = 'OL'
        # ECH entities
        elif aidtype in ['ECH']:
            self.change_appl('Configure')
            self.click("_ECI;tree")
            typeeqpt = 'ECI'
        # Special cables entities - filter and protection
        elif aidtype in ['FC', 'PC']:
            self.change_appl('Configure')
            # Expand tree
            self.try_click("//img[contains(@class,'Closed') and ../span/span[@id='_SCS;tree']]")
            if aidtype == 'FC':
                self.click("_FCS;tree")
                typeeqpt = 'FC'
            elif aidtype == 'PC':
                self.click("_PCS;tree")
                typeeqpt = 'PC'
        elif aidtype == 'SHELF':
            loc = "//*[@id='_SHELF-%s;tree']/span" % shelf
            self.click(loc)
            typeeqpt = self.get_value_loc(loc)
            typeeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', typeeqpt]
        else:
            try:
                # Expand tree
                self.try_click("//img[contains(@class,'Closed') and ../span/span[@id='_SHELF-%s;tree']]" % shelf)
                # Reading Type equipment of shelf or module
                # read Shelf type
                loc = "//*[@id='_SHELF-%s;tree']/span" % shelf
                typeeqpt = self.get_value_loc(loc)
                typeeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', typeeqpt]
                # read module type
                if (module and typeeqpt not in ['EROADM-DC']) or aidtype == 'FCU':
                    if module == 'FCU' or aidtype == 'FCU':
                        loctype = "//span[@id='_FCU-%s;tree']/span" % shelf
                    else:
                        loctype = "//span[@id='_MOD-%s-%s;tree']/span" % (shelf, module)
                    typeeqpt = self.get_value_loc(loctype)
                    typeeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', typeeqpt]
            except:
                # if module is not present in current view (Monitor or Maintain appl)
                self.change_appl('Configure')
                # Expand tree
                self.try_click("//img[contains(@class,'Closed') and ../span/span[@id='_SHELF-%s;tree']]" % shelf)
                # Reading Type equipment of shelf or module
                # read Shelf type
                loc = "//*[@id='_SHELF-%s;tree']/span" % shelf
                typeeqpt = self.get_value_loc(loc)
                typeeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', typeeqpt]
                # read module type
                if (module and typeeqpt not in ['EROADM-DC']) or aidtype == 'FCU':
                    if module == 'FCU' or aidtype == 'FCU':
                        loctype = "//span[@id='_FCU-%s;tree']/span" % shelf
                    else:
                        loctype = "//span[@id='_MOD-%s-%s;tree']/span" % (shelf, module)
                    if loctype in self:
                        # typeeqpt = self.get_value_loc(loctype)
                        # typeeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', typeeqpt]
                        # fix for card e.g. OSFM+#1510
                        typeeqpt_ned = self.get_value_loc(loctype)
                        typeeqpt_exist = self.typeeqpt_ned2exist(typeeqpt_ned)
                        typeeqpt = self._jsdata.name2val[
                            'TYPE__EQUIPMENT', typeeqpt_exist]

        # Check if configure dictionary has this aid and param
        if (param, typeeqpt) in self._jsdata.configure:
            applname, blade = self._seek_configure(aid, param, typeeqpt)
            if blade is None and (param, typeeqpt) in self._jsdata.configure_detail:
                applname, blade = self._seek_configure_detail(aid, param, typeeqpt)
        elif (param, typeeqpt) in self._jsdata.configure_detail:
            applname, blade = self._seek_configure_detail(aid, param, typeeqpt)
        elif (param, typeeqpt) in self._jsdata.maintain:
            applname, blade = self._seek_maintain(aid, param, typeeqpt)
        elif (param, typeeqpt) in self._jsdata.monitor or \
                any(prefix in param for prefix in ['__15MIN', '__24HOUR', '__1WEEK']):
            applname, blade = self._seek_monitor(aid, param, typeeqpt, history)
        else:
            raise RuntimeError('Parameter %s not found in any application for module %s;aid %s'
                               % (param, typeeqpt, aid))

        # switch to edit mode
        if edit and applname != 'Maintain' and not config_detail:
            if applname == 'Monitor':
                # Show thresholds enabled default
                if not self.driver.execute_script('return window.webgui.showAllCells'):
                    self.click('toggle-threshold')
                # wait until NED load parameters
                self._wait_loading()
                # Edit button in specific blade
                loc = "//div[div/div/span='%s']//a[contains(text(),'Edit')]" % blade
                if self.try_click(loc):
                    # wait until NED change all parameters to edit mode
                    self._wait_loading()
                return applname, blade
            if aidtype in ['MOD', 'SHELF']:
                # there is no blades under modules/shelfs - findig Edit button
                loc = "//div[div//*[@*='_%s;%s']]//a[text()='Edit']" % (aid, param)
                self.try_click(loc)
                # wait until NED change all parameters to edit mode
                self._wait_loading()
            else:
                # Edit button in specific blade
                loc = "//div[div/div/span='%s']//a[contains(text(),'Edit')]" % blade
                if self.try_click(loc):
                    # wait until NED change all parameters to edit mode
                    self._wait_loading()

                # Exception for LANE1__PROVISION (OTL)
                if param in ['LANE1__PROVISION']:
                    loc = "//div[../../span[@id='_%s;EP_PORT_INDEX'] and contains(.,'+')]" % aid
                    self.try_click(loc)
                    # wait until NED load parameters
                    self._wait_loading()
                if typeeqpt == "OL":
                    # open deatils window
                    loc = "//td[span[@id[contains(.,'_%s;EP_AID')]]]" % aid
                    if not self.try_click(loc):
                        loc = "//td[span[@id[contains(.,'_%s')]]]" % aid
                        self.try_click(loc)
                    # wait until NED load parameters
                    self._wait_loading()
        return applname, blade

    def _seek_configure(self, aid, param, typeeqpt):
        """Search in configure
        """
        applname, blade = 'Configure', ""
        aidtype, port = None, ''
        aidtype = aid.split('-')[0]

        if aidtype in ['CRS_FLW']:
            shelf = aid[8:].split('-')[1]
            module = aid[8:].split('-')[2]
        else:
            if len(aid.split('-')) >= 2:
                shelf = aid.split('-')[1]
            if len(aid.split('-')) >= 3:
                module = aid.split('-')[2]
            if len(aid.split('-')) >= 4:
                port = aid.split('-')[3]

        self.change_appl('Configure')
        # Expand tree
        self.try_click("//img[contains(@class,'Closed') and ../span/span[@id='_SHELF-%s;tree']]" % shelf)
        if aidtype == 'SHELF':
            loc = "//*[@id='_SHELF-%s;tree' and @aria-selected='false']/span" % shelf
            self.try_click(loc)
        else:
            # read shelf type
            locshelf = "//*[@id='_SHELF-%s;tree']/span" % shelf
            shelfeqpt = self.get_value_loc(locshelf)
            shelfeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', shelfeqpt]
            if (module and shelfeqpt not in ['EROADM-DC']) or aidtype == 'FCU':
                if module == 'FCU' or aidtype == 'FCU':
                    loc = "//span[@id='_FCU-%s;tree' and @aria-selected='false']/span" % shelf
                else:
                    loc = "//span[@id='_MOD-%s-%s;tree' and @aria-selected='false']/span" % (shelf, module)
                self.try_click(loc)
            else:
                self.try_click(locshelf)
        self._wait_loading()
        # used for optojacks (FPL, FCH)
        aidtype_tmp = ""

        # naming in NED js
        if re.match(r'[CN]\d+', port):
            port = re.sub(r'\d+', 'x', port)
        elif re.match(r'^\d+', port):
            port = ''
        elif re.match(r'^N', port):
            port = 'Nx'

        if aidtype == "FPL":
            aidtype_tmp = "FPL"
            aidtype = "PL"
        elif aidtype == "FCH":
            aidtype_tmp = "FCH"
            if typeeqpt in ['2PCA10G', '10PCA10G']:
                aidtype = "ETH"
            else:
                aidtype = "CH"

        js_dict = self._jsdata.configure
        # looking for parameter for specific typeeqpt
        if (param, typeeqpt) in js_dict:
            for key in [port, '', 'WIDGET']:
                try:
                    blade = js_dict[param, typeeqpt][aidtype, key]
                    break
                except KeyError:
                    pass
            else:
                if aidtype in ['ETH', 'VETH']:
                    if ('ETH+VETH', port) in js_dict[param, typeeqpt]:
                        blade = js_dict[param, typeeqpt]['ETH+VETH', port]
                    elif ('ETH+VETH', '') in js_dict[param, typeeqpt]:
                        blade = js_dict[param, typeeqpt]['ETH+VETH', '']
                    else:
                        # looking for table name in config details
                        return self._seek_configure_detail(aid, param, typeeqpt)
                elif aidtype in ['BRG']:
                    blade = js_dict['EP_AID', typeeqpt]['BRIDGE', port]
                elif aidtype in ['VCH', 'VSCH', 'VCH1']:
                    for key in [('VCH1', 'WIDGET'), ('VCH+VSCH', ''),
                                ('VCH', 'WIDGET'), ('VCH', '')]:
                        try:
                            blade = js_dict[param, typeeqpt][key]
                            break
                        except KeyError:
                            pass
                    else:
                        return self._seek_configure_detail(aid, param, typeeqpt)
                else:
                    return self._seek_configure_detail(aid, param, typeeqpt)
        else:
            # looking for table name in config details
            return self._seek_configure_detail(aid, param, typeeqpt)

        # Exceptions:
        if typeeqpt in ['4TCA4GUS', '4TCA4G', '10TCC10G'] and aidtype in ['CH']:
            for key in ['Ports', 'Data Channels']:
                if "//div[span='%s']/.." % key in self:
                    blade = key
                    break
        elif 'AES' in typeeqpt and aidtype in ['CH']:
            for key in ['Ports', 'Port Encryption', 'Data Channels']:
                if "//div[span='%s']/.." % key in self:
                    blade = key
                    break
        elif aidtype == "LINK" and "-SER" in aid:
            blade = "Serial Port"
        # End of exceptions

        # Open proper blade
        if aidtype not in ['MOD', 'SHELF']:
            if self.try_click("(//div[div[span='%s'] and contains(@class,'dijitClosed')])[last()]" % blade):
                self._wait_loading()
        # show far end entities
        if aidtype_tmp in ['FPL', 'FCH']:
            loc = "//div[../../../span[@id='_%s-%s;EP_PORT_INDEX'] and contains(.,'+')]" % (aidtype, aid[4:])
            self.click(loc)
            self._wait_loading()
        # show all channels if any filter occurs
        if aidtype in ['WCH', 'OWLG']:
            self.click("//table[@id='_opticalchannels;filter']")
            loc = "//div[@id='_opticalchannels;filter_menu']/table/tbody/tr[td='OL-%s']" % aid.split('-')[1]
            if loc in self:
                ActionChains(self.driver).move_to_element(self[loc]).perform()
                ActionChains(self.driver).move_to_element(self[loc]).click().perform()
                self._wait_loading()
        elif aidtype in ['FLW', 'CRS_FLW']:
            key = "_pointtopointpacketflowsevc;filter"
            if aidtype == 'FLW':
                eth_port = "ETH-" + '-'.join(aid.split('-')[1:4])
            else:
                eth_port = "ETH-" + '-'.join(aid.split('-')[2:5])
            self.click("//table[@id='%s']" % key)
            loc = "//div[@id='%s_menu']/table/tbody/tr[td='%s']" % (key, eth_port)
            if loc in self:
                ActionChains(self.driver).move_to_element(self[loc]).perform()
                ActionChains(self.driver).move_to_element(self[loc]).click().perform()
                self._wait_loading()
            if aidtype in ["CRS_FLW"]:
                loc = "//div[../../span[@id='_%s;SVID'] and contains(.,'+')]" % (aid[8:].split(',')[0])
                self.click(loc)
        else:
            for key in ['opticalchannels', 'datachannels']:
                if "//table[@id='_%s;filter']" % key in self:
                    self.click("//table[@id='_%s;filter']" % key)
                    loc = "//div[@id='_%s;filter_menu']/table/tbody/tr[td='All']" % key
                    if loc in self:
                        ActionChains(self.driver).move_to_element(self[loc]).perform()
                        ActionChains(self.driver).move_to_element(self[loc]).click().perform()
                        self._wait_loading()
        # wait until NED load parameters
        # if needed expose dependent entities (rows)
        loc = "//div[../../span[@id='_%s;EP_PORT_INDEX'] and contains(.,'+')]" % aid
        self.try_click(loc)
        return applname, blade

    def _seek_configure_detail(self, aid, param, typeeqpt):
        """Search in config deatils
        """
        applname, blade = 'Configure', ""
        aidtype, port = None, ''
        aidtype = aid.split('-')[0]
        if aidtype in ['CRS_FLW']:
            shelf = aid[8:].split('-')[1]
            module = aid[8:].split('-')[2]
        else:
            if len(aid.split('-')) >= 2:
                shelf = aid.split('-')[1]
            if len(aid.split('-')) >= 3:
                module = aid.split('-')[2]
            if len(aid.split('-')) >= 4:
                port = aid.split('-')[3]

        self.change_appl('Configure')
        # Expand tree
        self.try_click("//img[contains(@class,'Closed') and ../span/span[@id='_SHELF-%s;tree']]" % shelf)
        if aidtype == 'SHELF':
            loc = "//*[@id='_SHELF-%s;tree' and @aria-selected='false']/span" % shelf
            self.try_click(loc)
        else:
            # read shelf type
            locshelf = "//*[@id='_SHELF-%s;tree']/span" % shelf
            shelfeqpt = self.get_value_loc(locshelf)
            shelfeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', shelfeqpt]
            if (module and shelfeqpt not in ['EROADM-DC']) or aidtype == 'FCU':
                if module == 'FCU' or aidtype == 'FCU':
                    loc = "//span[@id='_FCU-%s;tree' and @aria-selected='false']/span" % shelf
                else:
                    loc = "//span[@id='_MOD-%s-%s;tree' and @aria-selected='false']/span" % (shelf, module)
                self.try_click(loc)
            else:
                self.try_click(locshelf)

        # used for optojacks (FPL, FCH)
        aidtype_tmp = ""
        # naming in NED js
        if re.match(r'[CN]\d+', port):
            port = re.sub(r'\d+', 'x', port)
        elif re.match(r'^\d+', port):
            port = ''
        elif re.match(r'^N', port):
            port = 'Nx'

        if aidtype == "FPL":
            aidtype_tmp = "FPL"
            aidtype = "PL"
        elif aidtype == "FCH":
            aidtype_tmp = "FCH"
            if typeeqpt in ['2PCA10G', '10PCA10G']:
                aidtype = "ETH"
            else:
                aidtype = "CH"

        js_dict = self._jsdata.configure
        js_detail = self._jsdata.configure_detail

        # Exception for OPT/OPR on AMP - it should be searched in monitor appl
        if typeeqpt in ['AMP-SHGCV', 'AMP-SLGCV', '9ROADM-C96', '4ROADM-C96', '4ROADM-E-C96'] and \
           param in ['OPR', 'OPT', 'EP_OPT', 'EP_OPR']:
            return self._seek_monitor(aid, param, typeeqpt)
        # go to proper blade (looking for EP_AID)
        if aidtype not in ['MOD', 'SHELF']:
            for key in [port, '', 'WIDGET']:
                try:
                    blade = js_dict['EP_AID', typeeqpt][aidtype, key]
                    break
                except KeyError:
                    pass
            else:
                if aidtype in ['ETH', 'VETH']:
                    blade = js_dict['EP_AID', typeeqpt]['ETH+VETH', '']
                elif aidtype in ['VCH', 'VSCH', 'VCH1']:
                    for key in [('VCH1', 'WIDGET'), ('VCH+VSCH', ''), ('VCH+VCH1', ''),
                                ('VCH+VSCH', ''), ('VCH', 'WIDGET'), ('VCH', '')]:
                        try:
                            blade = js_dict['EP_AID', typeeqpt][key]
                            break
                        except KeyError:
                            pass
                elif 'FFP' in aidtype:
                    blade = js_dict['WKG-AID', typeeqpt][aidtype, '']
                elif aidtype in ['CRS_FLW']:
                    blade = js_dict['CRS-FROM-AID', typeeqpt]['FLW', 'WIDGET']
                else:
                    return applname, None

            # Exceptions:
            if typeeqpt in ['4TCA4GUS', '4TCA4G', '10TCC10G'] and aidtype in ['CH']:
                for key in ['Ports', 'Data Channels']:
                    if "//div[span='%s']/.." % key in self:
                        blade = key
                        break
            elif 'AES' in typeeqpt and aidtype in ['CH']:
                for key in ['Ports', 'Port Encryption', 'Data Channels']:
                    if "//div[span='%s']/.." % key in self:
                        blade = key
                        break
            elif aidtype == "LINK" and "-SER" in aid:
                blade = "Serial Port"
            # End of exceptions

            # open proper blade
            if self.try_click("(//div[div[span='%s'] and contains(@class,'dijitClosed')])[last()]" % blade):
                self._wait_loading()
            # show far end entities
            if aidtype_tmp in ['FPL', 'FCH']:
                loc = "//div[../../../span[@id='_%s-%s;EP_PORT_INDEX'] and contains(.,'+')]" % (aidtype, aid[4:])
                self.click(loc)
            # show all ROADMs Optical channels
            if "//table[@id='_opticalchannels;filter']" in self:
                self.click("//table[@id='_opticalchannels;filter']")
                loc = "//div[@id='_opticalchannels;filter_menu']/table/tbody/tr[td='All']"
                if loc in self:
                    ActionChains(self.driver).move_to_element(self[loc]).perform()
                    ActionChains(self.driver).move_to_element(self[loc]).click().perform()

            if aidtype in ['FLW', 'CRS_FLW']:
                key = "_pointtopointpacketflowsevc;filter"
                if aidtype == 'FLW':
                    eth_port = "ETH-" + '-'.join(aid.split('-')[1:4])
                else:
                    eth_port = "ETH-" + '-'.join(aid.split('-')[2:5])
                self.click("//table[@id='%s']" % key)
                loc = "//div[@id='%s_menu']/table/tbody/tr[td='%s']" % (key, eth_port)
                if loc in self:
                    ActionChains(self.driver).move_to_element(self[loc]).perform()
                    ActionChains(self.driver).move_to_element(self[loc]).click().perform()
                    self._wait_loading()
                if aidtype in ["CRS_FLW"]:
                    loc = "//div[../../span[@id='_%s;SVID'] and contains(.,'+')]" % (aid[8:].split(',')[0])
                    self.click(loc)
            # wait until NED load parameters
            self._wait_loading()

        # look for blade in config details
        if (param, typeeqpt) in self._jsdata.configure_detail:
            if (aidtype, port) in js_detail[param, typeeqpt]:
                blade = js_detail[param, typeeqpt][aidtype, port]
            elif (aidtype, '') in js_detail[param, typeeqpt]:
                blade = js_detail[param, typeeqpt][aidtype, '']
            else:
                return applname, None
        else:
            return applname, None

        # open deatils window
        loc = "//td[span[@id[contains(.,'_%s;EP_AID')]]]" % aid
        if not self.try_click(loc):
            loc = "//td[span[@id[contains(.,'_%s')]]]" % aid
            self.try_click(loc)
        # wait until NED load parameters
        self._wait_loading()

        # open blade
        if self.try_click("(//div[div[span='%s'] and contains(@class,'dijitClosed')])[last()]" % blade):
            self._wait_loading()
        return applname, blade

    def _seek_maintain(self, aid, param, typeeqpt):
        """Search in maintain
        """
        applname, blade = 'Maintain', ""
        aidtype, shelf, module, port = None, None, None, None
        aidtype = aid.split('-')[0]
        if len(aid.split('-')) >= 2:
            shelf = aid.split('-')[1]
        if len(aid.split('-')) >= 3:
            module = aid.split('-')[2]
        if len(aid.split('-')) >= 4:
            port = aid.split('-')[3]

        # change application to Maintain
        self.change_appl('Maintain')

        js_dict = self._jsdata.maintain

        # Expanding shelf tree
        self.try_click("//img[contains(@class,'Closed') and ../span/span[@id='_SHELF-%s;tree']]" % shelf)
        if aidtype == 'SHELF':
            loc = "//*[@id='_SHELF-%s;tree' and @aria-selected='false']/span" % shelf
            self.try_click(loc)

        if module and typeeqpt not in ['EROADM-DC']:
            if module in ['FCU']:
                loc = "//span[@id='_FCU-%s;tree' and @aria-selected='false']/span" % shelf
            else:
                loc = "//span[@id='_MOD-%s-%s;tree' and @aria-selected='false']/span" % (shelf, module)
            self.try_click(loc)
        elif module and typeeqpt in ['EROADM-DC']:
            loc = "//*[@id='_SHELF-%s;tree' and @aria-selected='false']/span" % shelf
            self.try_click(loc)
            port = aid.split('-')[2]

        # retrive group and table - only two possibilities - pure except used
        try:
            radio, blade = js_dict[param, typeeqpt][aidtype, port].split(';')
        except:
            radio, blade = js_dict[param, typeeqpt][aidtype, ''].split(';')

        # open blade and choose radio button for specific group
        if blade:
            if self.try_click("(//div[div[span='%s'] and contains(@class,'dijitClosed')])[last()]" % blade):
                self._wait_loading()
            loc = "//div[div/div[span='%s']]//li[label[contains(text(),'%s')]]/input" % (blade, radio)
            self.try_click(loc)
        else:
            loc = "//li[label[contains(text(),'%s')]]/input" % radio
            self.try_click(loc)
        self._wait_loading()

        return applname, blade

    def _seek_monitor(self, aid, param, typeeqpt, history=False):
        """Search in monitor

        historical pm's are still missing
        """
        applname, blade = 'Monitor', ""
        aidtype, shelf, module, port = None, None, None, None
        radio = ""
        aidtype = aid.split('-')[0]
        if len(aid.split('-')) >= 2:
            shelf = aid.split('-')[1]
        if len(aid.split('-')) >= 3:
            module = aid.split('-')[2]
        if len(aid.split('-')) >= 4:
            port = aid.split('-')[3]

        # change application to Maintain
        self.change_appl('Monitor')

        js_dict = self._jsdata.monitor
        # naming in NED js
        if re.match(r'[CN]\d+', port):
            port = re.sub(r'\d+', 'x', port)
        elif re.match(r'^\d+', port):
            port = ''
        elif re.match(r'^N', port):
            port = 'Nx'

        # Expanding shelf tree
        self.try_click("//img[contains(@class,'Closed') and ../span/span[@id='_SHELF-%s;tree']]" % shelf)
        if aidtype == 'SHELF':
            loc = "//*[@id='_SHELF-%s;tree' and @aria-selected='false']/span" % shelf
            self.try_click(loc)
        else:
            # read shelf type
            locshelf = "//*[@id='_SHELF-%s;tree']/span" % shelf
            shelfeqpt = self.get_value_loc(locshelf)
            shelfeqpt = self._jsdata.name2val['TYPE__EQUIPMENT', shelfeqpt]
            if module and shelfeqpt not in ['EROADM-DC']:
                if module in ['FCU']:
                    loc = "//span[@id='_FCU-%s;tree' and @aria-selected='false']/span" % shelf
                else:
                    loc = "//span[@id='_MOD-%s-%s;tree' and @aria-selected='false']/span" % (shelf, module)
                self.try_click(loc)
            elif module and shelfeqpt in ['EROADM-DC']:
                self.try_click(locshelf)
                port = aid.split('-')[2]
        self._wait_loading()

        # set time period
        if '__15MIN' in param:
            timeperiod = '15 Minutes'
        elif '__24HOUR' in param:
            timeperiod = 'Daily'
        elif '__1WEEK' in param:
            timeperiod = 'Weekly'
        else:
            timeperiod = 'Latest'

        # wait until NED load parameters
        self._wait_loading()
        # Current 15MIN, 24HOUR, 1WEEK, thresholds excluded
        if any(suffix in param for suffix in ['__15MIN', '__24HOUR', '__1WEEK']) and \
           not any(suffix in param for suffix in ['-FLT', '-FHT', '-LT', '-HT']):
            if any(prefix in param for prefix in ['OPR', 'OPT', 'OSCOPT', 'OSCPWR']):
                try:
                    val = js_dict['EP_' + param.split('__')[0].split('-')[0], typeeqpt][aidtype, port]
                except:
                    val = js_dict['EP_' + param.split('__')[0].split('-')[0], typeeqpt][aidtype, '']
                radio, blade = val.split(';')
            else:
                for par in [param.split('-')[0], param.split('__')[0]]:
                    for key in [port, '']:
                        try:
                            radio, blade = js_dict[par, typeeqpt][aidtype, key].split(';')
                            break
                        except KeyError:
                            pass
        elif param == "EP_RESET_PM_DL_COUNTERS":
            try:
                radio, blade = js_dict['EP_AID', typeeqpt][aidtype, port].split(';')
            except:
                radio, blade = js_dict['EP_AID', typeeqpt][aidtype, ''].split(';')
        else:
            for par in [param, param.split('-')[0], 'EP_'+param]:
                for key in [port, '']:
                    try:
                        radio, blade = js_dict[par, typeeqpt][aidtype, key].split(';')
                        break
                    except KeyError:
                        pass

        # remove unnecessary suffixes
        if ' - History' in blade:
            blade = blade.split(' - History')[0]
        elif ' - Physical' in blade:
            blade = blade.split(' - Physical History')[0]

        # open proper blade
        if aidtype not in ['MOD', 'SHELF']:
            if self.try_click("(//div[div[span='%s'] and contains(@class,'dijitClosed')])[last()]" % blade):
                self._wait_loading()

        # if necessary switch to historical PMs:
        if history:
            tab = "History"
        else:
            if param == "EP_RESET_PM_DL_COUNTERS":
                tab = 'Clear Counters'
            else:
                tab = "Current"
        loc = "//div[div/div/span='%s']//div[span='%s']" % (blade, tab)
        self.click(loc)
        self._wait_loading()
        # finishing method for Clear Counters
        if param == "EP_RESET_PM_DL_COUNTERS":
            return applname, blade
        # choose time period
        loc = "//div[div/div/span='%s']//div[span[text()='%s'] and contains(@id,'%s')]" % (blade, timeperiod, tab)
        self.click(loc)
        self._wait_loading()
        # choose port/channel in PMs history
        if history:
            script = "return window.webgui.monitor.aid2label['%s']" % aid
            aidlabel = self.driver.execute_script(script)
            select_name = "%s-select" % re.sub(r'[^\w]', '', blade).lower()
            loc = "//table[@id='%s']" % select_name
            self.click(loc)
            loc = "//div[@id='%s_menu']/table/tbody/tr[td='%s']" % (select_name, aidlabel)
            if loc in self:
                self[loc].location_once_scrolled_into_view
                self.click(loc)

        # choose radio button - radio button with $x("//label[text()=\"\u00a0OTU\"]") - nbsp spaces
        loc = ("//div[div/div/span='%s']//div[@title='%s']//li[label[substring(text(),2) = '%s']]"
               "/input[contains(@id,'%s')]" % (blade, timeperiod, radio, tab))

        if not self.try_click(loc):
            loc = ("//div[div/div/span='%s']//div[contains(@id,'%s')]//li[label[substring(text(),2) = '%s']]"
                 "/input[contains(@id,'%s')]" % (blade, timeperiod, radio, tab))
            self.try_click(loc)
            self._wait_loading()
        return applname, blade

    def _seek_node(self, aid, param, value, edit=False):
        """ Node is created in static way
        """
        applname, blade = "Node", ""
        self.change_appl('Node')
        try:
            if param in ['MODEL', 'VENDOR', 'NETYPE', 'ALIAS', 'SID',
                         'LOCATION', 'CONTACT', 'RACKSIZE']:
                blade = '_general;information'
                self.click("//span[span='Information']")
            elif param in ['WEBREDIR', 'SNMP', 'TL1', 'SNMP-V1', 'SNMP-V3']:
                blade = '_general;controls;interfaces'
                self.click("//span[span='Controls']")
            elif param in ['AISPENA', 'AISPDEFTM']:
                blade = '_general;controls;automaticin-service'
                self.click("//span[span='Controls']")
            elif param in ['EQLZ-ADMIN', 'EQLZ-INVL', 'EQLZDAT', 'EQLZTM']:
                blade = '_general;controls;scheduledequalization'
                self.click("//span[span='Controls']")
            elif param in ['FORCE-DLT', 'AUTOP', 'SIGDEF', 'SCU-RING', 'FIBER-DETECT']:
                blade = '_general;controls;functionality'
                self.click("//span[span='Controls']")
            elif param in ['AAT', 'ADT']:
                blade = '_general;defaults;alarm'
                self.click("//span[span='Defaults']")
            elif param in ['FRCDOPDEFTM']:
                blade = '_general;defaults;laserforcetimer'
                self.click("//span[span='Defaults']")
            elif param in ['SES-SDH', 'SES-OTN']:
                blade = '_general;defaults;severelyerroredseconds'
                self.click("//span[span='Defaults']")
            elif param in ['AUTH-TRAPS', 'EXT-AUTH-TRAPS', 'SECURE-SNMP-V3', 'UDPPORT']:
                blade = '_general;snmp;configuration'
                self.click("//span[span='SNMP']")
            elif param in ['SECURITY-MODE', 'PID-MIN-LENGTH', 'PID-HISTORY-SIZE',
                           'LOGIN-FAIL-DELAY', 'SHOW-LAST-LOGIN-SUCCESS', 'SHOW-LAST-LOGIN-FAIL']:
                blade = '_security;access;passwordmanagement'
                query = "//span[text()='Security' and @aria-expanded='false']"
                self.try_click(query)
                self.click("//span[span='Access']")
            elif param in ['REMOTEAUTH', 'FTPC', 'FTP', 'SSHD', 'TELNET', 'BOOTLOADER_ACCESS',
                           'SYSINFO-PRELOGIN', 'SNMP-WRITE-ACCESS']:
                blade = '_security;access;accessmanagement'
                query = "//span[text()='Security' and @aria-expanded='false']"
                self.try_click(query)
                self.click("//span[span='Access']")
            elif param in ['ACCESS_WARNING', 'ACCESS_WARNINGMSG']:
                blade = '_security;access;warningmessage'
                query = "//span[text()='Security' and @aria-expanded='false']"
                self.try_click(query)
                self.click("//span[span='Access']")
            elif param in ['CRAFT_SESS-TMOUT', 'SER_TELNET_LOG-TMOUT', 'SSH_LOG-TMOUT', 'WEBGUI_SESS-TMOUT',
                           'TL1_LOG-TMOUT', 'SNMP_SESS-TMOUT', 'SNMP-WRITE-REQUEST-TMOUT']:
                blade = '_security;access;timeouts'
                query = "//span[text()='Security' and @aria-expanded='false']"
                self.try_click(query)
                self.click("//span[span='Access']")
            elif "MOD" in aid or "EQPT-UBR" in aid:
                # go to firmware table
                blade = '_software;module'
                query = "//span[text()='Software' and @aria-expanded='false']"
                self.try_click(query)
                self.click("//span[span='Module']")
                # wait for grid to load
                time.sleep(2)
            elif "SRV-UBR" in aid or 'DATA-UBR' in aid:
                if param in ['GDBISSUE', 'CRDAT', 'CRTM']:
                    # go to database
                    blade = '_database;information'
                    query = "//span[text()='Database' and @aria-expanded='false']"
                    self.try_click(query)
                    self.click("//div[div/span/span[text()='Database']]//span[span='Information']")
                elif param == 'COMMAND__NCU' and value in ['BACKUP']:
                    blade = '_database;backup'
                    query = "//span[text()='Database' and @aria-expanded='false']"
                    self.try_click(query)
                    self.click("//div[div/span/span[text()='Database']]//span[span='Backup']")
                elif param == 'COMMAND__NCU' and value in ['REBOOT', 'RESTORE']:
                    blade = '_database;mange'
                    query = "//span[text()='Database' and @aria-expanded='false']"
                    self.try_click(query)
                    self.click("//div[div/span/span[text()='Database']]//span[span='Manage']")
                elif param == 'COMMAND__NCU' and \
                        value in ['IMPORT_ALP', 'EXPORT_ALP', 'ACTIVATE_ALP', 'ACTIVATE_FD_ALP']:
                    blade = '_profiles;alarm'
                    query = "//span[text()='Profiles' and @aria-expanded='false']"
                    self.try_click(query)
                    self.click("//div[div/span/span[text()='Profiles']]//span[span='Alarm']")
                else:
                    # go to software table
                    blade = '_software;ncu'
                    query = "//span[text()='Software' and @aria-expanded='false']"
                    self.try_click(query)
                    self.click("//span[span='NCU']")
            elif "COPY-UBR" in aid:
                # go to file storage table
                blade = 'general;filestorage'
                self.click("//span[span='File Storage']")
            elif aid in ['TIME-NTP']:
                blade = '_general;date-time;date&time'
                self.click("//span[span='Date & Time']")
            elif 'NTPSRV-' in aid:
                blade = '_general;date-time;networktimeprotocol(ntp)servers'
                self.click("//span[span='Date & Time']")
            elif 'REMAUTH-' in aid:
                self.click("//span[span='Node']")
                blade = '_security;access;radius'
                query = "//span[text()='Security' and @aria-expanded='false']"
                self.try_click(query)
                self.click("//span[span='Access']")
                if edit:
                    query = "//span[@id='_%s%s;%s']" % (int(aid[-1]) - 1, aid, param)
                    self.try_click(query)
            # fake aid for LOGS:
            elif 'LOG' in aid:
                query = "//span[text()='Logs' and @aria-expanded='false']"
                self.try_click(query)
                self.click("//span[span='%s']" % param)
                # wait for grid to load
                time.sleep(2)
                blade = param
            # SPEQ moved into Summary
            elif param in ['SPEQ-CONF', 'DYNAMIC-COMP']:
                self.change_appl('Summary')
                blade = ("__span-equalization;spanequalization-"
                         "identifiesandcontrolsthegainofamplifiersassociatedwithnetworkfibers")
                self.click("//span[span='Span Equalization']")
                return 'Summary', blade

        except NoSuchElementException as ex:
            raise RuntimeError(ex.msg)

        if not blade:
            raise RuntimeError('Parameter %s not found on aid %s' % (param, aid))
        return applname, blade

        def typeeqpt_ned2exist(self, typeeqpt_ned):
            '''
            this method handles cases if a typeeqpt is not defined in self._jsdata
            typeeqpt_ned: typeeqpt on NED
            returns an existing typeeqpt in self._jsdata
            '''
            typeeqpt_new_to_exist = {
                'EDFA-C-S20-GCB-DM': 'EDFA-SGCB',
                'OSFM+#1510': 'OSFM'
            }

            try:
                typeeqpt_exist = typeeqpt_new_to_exist[typeeqpt_ned]
            except KeyError:
                typeeqpt_exist = typeeqpt_ned

            return typeeqpt_exist
