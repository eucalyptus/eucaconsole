
/**
 * @Author : Florent BREHERET
 * @Function : Activate an implicite wait on action commands when trying to find elements.
 * @Param timeout : Timeout in millisecond, set 0 to disable the implicit wait
 * @Exemple 1 : setImplicitWaitLocator | 0
 * @Exemple 1 : setImplicitWaitLocator | 1000
 */
Selenium.prototype.doSetImplicitWaitLocator = function(timeout){
        if( timeout== 0 ) {
                implicitwait.locatorTimeout=0;
                implicitwait.isImplicitWaitLocatorActivated=false;
        }else{
                implicitwait.locatorTimeout=parseInt(timeout);
                implicitwait.isImplicitWaitLocatorActivated=true;
        }
};

/**
 * @author : Florent BREHERET
 * @Function : Activate an implicite wait for condition before commands are executed.
 * @Param timeout : Timeout in millisecond, set 0 to disable the implicit wait
 * @Param condition_js : Javascript logical expression that need to be true to execute each command.
 *
 * @Exemple 0 : setImplicitWaitCondition |  0  |  
 * @Exemple 1 : setImplicitWaitCondition |  1000  | (typeof window.Sys=='undefined') ? true : window.Sys.WebForms.PageRequestManager.getInstance().get_isInAsyncPostBack()==false;
 * @Exemple 2 : setImplicitWaitCondition |  1000  | (typeof window.dojo=='undefined') ? true : window.dojo.io.XMLHTTPTransport.inFlight.length==0;
 * @Exemple 3 : setImplicitWaitCondition |  1000  | (typeof window.Ajax=='undefined') ? true : window.Ajax.activeRequestCount==0;
 * @Exemple 4 : setImplicitWaitCondition |  1000  | (typeof window.tapestry=='undefined') ? true : window.tapestry.isServingRequests()==false;
 * @Exemple 4 : setImplicitWaitCondition |  1000  | (typeof window.jQuery=='undefined') ? true : window.jQuery.active==0;
 */
Selenium.prototype.doSetImplicitWaitCondition = function( timeout, condition_js ) {
        if( timeout==0 ) {
                implicitwait.conditionTimeout=0;
                implicitwait.implicitAjaxWait_Condition=null;
                implicitwait.isImplicitWaitAjaxActivated=false;
        }else{
                implicitwait.conditionTimeout=parseInt(timeout);
                implicitwait.implicitAjaxWait_Condition=condition_js;
                implicitwait.isImplicitWaitAjaxActivated=true;
        }
}

function ImplicitWait() {
        var self=this;
        this.isImplicitWaitLocatorActivated = false;
        this.isImplicitWaitAjaxActivated = false;
        this.implicitAjaxWait_Condition=null;
        this.conditionTimeout=0;
        this.locatorTimeout=0;
        this.isLogEnabled=true;
}

MozillaBrowserBot.prototype.findElement = function (locator, win){
        var element = this.findElementOrNull(locator, win);
        if (element == null) {
                throw {
                        isFindElementError: true,
                        message: "Element " + locator + " not found"
                }
        }
        return core.firefox.unwrap(element);
};

KonquerorBrowserBot.prototype.findElement = MozillaBrowserBot.prototype.findElement;
SafariBrowserBot.prototype.findElement = MozillaBrowserBot.prototype.findElement;
OperaBrowserBot.prototype.findElement = MozillaBrowserBot.prototype.findElement;
IEBrowserBot.prototype.findElement = MozillaBrowserBot.prototype.findElement;

ImplicitWait.resume_overrided = function() {
        try {
                var self=this;
                if(this.abord) return;
                if( !typeof htmlTestRunner === 'undefined'){
                        if(htmlTestRunner.controlPanel.runInterval == -1){
                                return this.continueTestAtCurrentCommand();
                        }
                }
                if (implicitwait.isImplicitWaitAjaxActivated && !this.currentCommand.implicitElementWait_EndTime) {
                        if( !this.currentCommand.implicitAjaxWait_EndTime ){
                                this.currentCommand.implicitAjaxWait_EndTime = (new Date().getTime() + parseInt(implicitwait.conditionTimeout * 0.8));
                                return window.setTimeout( function(){return self.resume.apply(self);}, 3);
                        }
                        if (new Date().getTime() > this.currentCommand.implicitAjaxWait_EndTime) {
                                throw new SeleniumError("Implicit wait timeout reached while waiting for condition \"" + implicitwait.implicitAjaxWait_Condition  + "\"");
                        }else{
                                var ret;
                                try{
                                        ret=eval(implicitwait.implicitAjaxWait_Condition);
                                        //ret = implicitwait.implicitAjaxWait_Function.call(htmlTestRunner.selDebugger.runner.selenium);
                                        //ret=(function(condition){return eval(condition);}).call(htmlTestRunner.selDebugger.runner.selenium, implicitwait.implicitAjaxWait_Condition)
                                } catch (e) {
                                        throw new SeleniumError("ImplicitWaitCondition failed : " + e.message );
                                }
                                if(!ret) return window.setTimeout( function(){return self.resume.apply(self);}, 20);
                        }
                }
                if(implicitwait.isImplicitWaitLocatorActivated){
                        if(!this.currentCommand.implicitElementWait_EndTime){
                                this.currentCommand.implicitElementWait_EndTime = (new Date().getTime() + parseInt(implicitwait.locatorTimeout * 0.8));
                        }
                }
                selenium.browserbot.runScheduledPollers();
                this._executeCurrentCommand();
                this.continueTestWhenConditionIsTrue();
        } catch (e) {
                if(e.isFindElementError){
                        if(implicitwait.isImplicitWaitLocatorActivated){
                                if( new Date().getTime() < this.currentCommand.implicitElementWait_EndTime){
                                        implicitwait.isLogEnabled = false;
                                        return window.setTimeout( function(){return self.resume.apply(self);}, 20);
                                }else{
                                        e = SeleniumError( "Implicit wait timeout reached. " + e.message );
                                }
                        }else{
                                e = SeleniumError( e.message );
                        }
                }
                implicitwait.isLogEnabled = true;
                if(!this._handleCommandError(e)){
                        this.testComplete();
                }else {
                        this.continueTest();
                }
        }
        implicitwait.isLogEnabled = true;
};

ImplicitWait.HookAnObjectMethodBefore = function(ClassObject, ClassMethod, HookClassObject, HookMethod) {
        if (ClassObject) {
                var method_id = ClassMethod.toString() + HookMethod.toString();
                if (!ClassObject[method_id]) {
                        ClassObject[method_id] = ClassObject[ClassMethod];
                        ClassObject[ClassMethod] = function() {
                                if( HookMethod.call(HookClassObject, ClassObject, arguments )==true ){
                                        return ClassObject[method_id].apply(ClassObject, arguments);
                                }
                        }
                        return true;
                }
        }
        return false;
};

try {
        var implicitwait = new ImplicitWait();
        ImplicitWait.HookAnObjectMethodBefore(LOG, 'log', implicitwait, function(){return implicitwait.isLogEnabled} );
        if( typeof RemoteRunner == 'function'){
                RemoteRunner.prototype.resume = ImplicitWait.resume_overrided;
        }
        if( typeof HtmlRunnerTestLoop == 'function'){
                HtmlRunnerTestLoop.prototype.resume = ImplicitWait.resume_overrided;
        }
} catch (error) {
        alert('Error in ImplicitWait: ' + error);
}



