
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



/***********************************************************************************/

/*
 (C) Copyright MetaCommunications, Inc. 2006.
     http://www.meta-comm.com
     http://engineering.meta-comm.com

Distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
*/

function map_list( list, for_func, if_func )
    {
    var mapped_list = [];
    for ( var i = 0; i < list.length; ++i )
        {
        var x = list[i];
        if( null == if_func || if_func( i, x ) )
            mapped_list.push( for_func( i, x ) );
        }
    return mapped_list;
    }

   
// Modified to initialize GoTo labels/cycles list
HtmlRunnerTestLoop.prototype.old_initialize = HtmlRunnerTestLoop.prototype.initialize

HtmlRunnerTestLoop.prototype.initialize = function(htmlTestCase, metrics, seleniumCommandFactory)
    {
    this.gotoLabels  = {};
    this.whileLabels = { ends: {}, whiles: {} };
   
    this.old_initialize(htmlTestCase, metrics, seleniumCommandFactory);
   
    this.initialiseLabels();
    }

HtmlRunnerTestLoop.prototype.initialiseLabels = function()
    {
    var command_rows = map_list( this.htmlTestCase.getCommandRows()
                               , function(i, x) {
                                    return x.getCommand()
                                    }
                               );

    var cycles = [];
    for( var i = 0; i < command_rows.length; ++i )
        {
        switch( command_rows[i].command.toLowerCase() )
            {
            case "label":
                this.gotoLabels[ command_rows[i].target ] = i;
                break;
            case "while":
            case "endwhile":
                cycles.push( [command_rows[i].command.toLowerCase(), i] )
                break;
            }
        }        
       
    var i = 0;
    while( cycles.length )
        {
        if( i >= cycles.length )
            throw new Error( "non-matching while/endWhile found" );
           
        switch( cycles[i][0] )
            {
            case "while":
                if(    ( i+1 < cycles.length )
                    && ( "endwhile" == cycles[i+1][0] )
                    )
                    {
                    // pair found
                    this.whileLabels.ends[ cycles[i+1][1] ] = cycles[i][1]
                    this.whileLabels.whiles[ cycles[i][1] ] = cycles[i+1][1]
                   
                    cycles.splice( i, 2 );
                    i = 0;
                    }
                else
                    ++i;
                break;
            case "endwhile":
                ++i;
                break;
            }
        }
                   
    }    

HtmlRunnerTestLoop.prototype.continueFromRow = function( row_num )
    {
    if(    row_num == undefined
        || row_num == null
        || row_num < 0
        )
        throw new Error( "Invalid row_num specified." );
       
    this.htmlTestCase.nextCommandRowIndex = row_num;
    }
   


// do nothing. simple label
Selenium.prototype.doLabel      = function(){};

Selenium.prototype.doGotolabel  = function( label ) {

    if( undefined == htmlTestRunner.currentTest.gotoLabels[label] )
        throw new Error( "Specified label '" + label + "' is not found." );
   
    htmlTestRunner.currentTest.continueFromRow( htmlTestRunner.currentTest.gotoLabels[ label ] );
    };
   
Selenium.prototype.doGoto = Selenium.prototype.doGotolabel;


Selenium.prototype.doGotoIf = function( condition, label ) {
    if( eval(condition) )
        this.doGotolabel( label );
    }


   
Selenium.prototype.doWhile = function( condition ) {
    if( !eval(condition) )
        {
        var last_row = htmlTestRunner.currentTest.htmlTestCase.nextCommandRowIndex - 1
        var end_while_row = htmlTestRunner.currentTest.whileLabels.whiles[ last_row ]
        if( undefined == end_while_row )
            throw new Error( "Corresponding 'endWhile' is not found." );
       
        htmlTestRunner.currentTest.continueFromRow( end_while_row + 1 );
        }
    }


Selenium.prototype.doEndWhile = function() {
    var last_row = htmlTestRunner.currentTest.htmlTestCase.nextCommandRowIndex - 1
    var while_row = htmlTestRunner.currentTest.whileLabels.ends[ last_row ]
    if( undefined == while_row )
        throw new Error( "Corresponding 'While' is not found." );
   
    htmlTestRunner.currentTest.continueFromRow( while_row );
    }

