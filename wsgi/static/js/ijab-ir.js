/*

 * ijab-ir.js -- IR Project: Google Search Enhance by Google+

 * Copyright (c) 2013 by IR Project Contributors
 * Published under the MIT license.

 * Author: iJab(Zhan Caibao)
 * EMail: ZHANCAIBAO(at)GMAIL.COM
 * Date: 04/09/2013

 */

var IJabIR = {
    /**
     * Constant: VERSION
     */
    VERSION: "Release 0.2",

    /**
     * Method: _getScriptLocation
     * Return the path to this script. 
     *
     * Returns:
     * {String} Path to this script
     */
    _getScriptLocation: (function() {
        var r = new RegExp("(^|(.*?\\/))(IJabIR[^\\/]*?\\.js)(\\?|$)"),
            s = document.getElementsByTagName('script'),
            src, m, l = "";
        for(var i=0, len=s.length; i<len; i++) {
            src = s[i].getAttribute('src');
            if(src) {
                m = src.match(r);
                if(m) {
                    l = m[1];
                    break;
                }
            }
        }
        return (function() { return l; });
    })()
};

/**
 * Constructor: IJabIR.Class
 * Implementation of OOP in Javascript with prototype mode with supporting 
 *     multiple inheritance. 
 * 
 * To create a new class in IJabIR, use the following syntax:
 * (code)
 *     var specificClass = IJabIR.Class(prototype);
 * (end)
 *
 * To create a new class with multiple inheritance, use the
 *     following syntax:
 * (code)
 *     var multInheritClass = IJabIR.Class(Class1, Class2, prototype);
 * (end)
 * 
 * Note that instanceof operation will only regard Class1 as superclass.
 *
 */
IJabIR.Class = function() 
{
    var len = arguments.length;
    var P = arguments[0];
    var F = arguments[len-1];

    var C = typeof F.initialize == "function" ?
        F.initialize :
        function(){ P.prototype.initialize.apply(this, arguments); };

    if (len > 1) 
    {
        var newArgs = [C, P].concat(
                Array.prototype.slice.call(arguments).slice(1, len-1), F);
        IJabIR.inherit.apply(null, newArgs);
    } 
    else 
    {
        C.prototype = F;
    }
    return C;
};

/**
 * Function: IJabIR.inherit
 *
 * Parameters:
 * C - {Object} the class that inherits
 * P - {Object} the superclass to inherit from
 *
 * In addition to the mandatory C and P parameters, an arbitrary number of
 * objects can be passed, which will extend C.
 */
IJabIR.inherit = function(C, P) 
{
   var F = function() {};
   F.prototype = P.prototype;
   C.prototype = new F;
   var i, l, o;
   for(i=2, l=arguments.length; i<l; i++) 
   {
       o = arguments[i];
       if(typeof o === "function") 
       {
           o = o.prototype;
       }
       IJabIR.Util.extend(C.prototype, o);
   }
};

/**
 * Util Function: extend
 * Copy all properties of a source object to a destination object.  Modifies
 *     the passed in destination object.  Any properties on the source object
 *     that are set to undefined will not be (re)set on the destination object.
 *
 * Parameters:
 * destination - {Object} The object that will be modified
 * source - {Object} The object with properties to be set on the destination
 *
 * Returns:
 * {Object} The destination object.
 */
IJabIR.Util = IJabIR.Util || {};
IJabIR.Util.extend = function(destination, source) 
{
    destination = destination || {};
    if (source)
    {
        for (var property in source)
        {
            var value = source[property];
            if (value !== undefined)
            {
                destination[property] = value;
            }
        }

        /**
         * IE doesn't include the toString property when iterating over an object's
         * properties with the for(property in object) syntax.  Explicitly check if
         * the source has its own toString property.
         */

        /*
         * FF/Windows < 2.0.0.13 reports "Illegal operation on WrappedNative
         * prototype object" when calling hawOwnProperty if the source object
         * is an instance of window.Event.
         */

        var sourceIsEvt = typeof window.Event == "function"
                          && source instanceof window.Event;

        if (!sourceIsEvt
           && source.hasOwnProperty && source.hasOwnProperty("toString")) 
        {
            destination.toString = source.toString;
        }
    }
    return destination;
};

/**
 * Class: IJabIR.Search
 *
 */
IJabIR.Search = IJabIR.Class(
{
		/**
     * Constructor: IJabIR.Search
     *
     * Parameters:
     * options - {Object} Hashtable of extra options
     */
    initialize: function(options) {
        IJabIR.Util.extend(this, options);
    },
    
    /*
     * Properties
     */
    baseURL							: "",

		/*
		 * Functions
		 */
		get_suggestion : function()
		{
		}
}

/**
 * Class: IJabIR.IM
 *
 */
IJabIR.IM = IJabIR.Class(
{
		/**
     * Constructor: IJabIR.Search
     *
     * Parameters:
     * options - {Object} Hashtable of extra options
     */
    initialize: function(options) {
        IJabIR.Util.extend(this, options);
    },
    
    /*
     * Properties
     */
    baseURL							: "",


		/*
		 * Functions
		 *
		 */
	  login : function()
	  {
	  	if(typeof iJab == undefined) return false;
	  	
	  	var userName = document.getElementById("login").value;
    	var password = document.getElementById("password").value;
    	if(userName == "" || password == "")
    	{
    		alert("username or password is empty!");
    	};    	
  		iJab.login(userName,password);
	  },
	  
	  logout : function()
	  {
	  	if(typeof iJab == undefined) return false;
	  	
	  	iJab.logout();
	  },
	  
	  bind_events : function()
	  {
	  	var self = this;
	  	/* Bind to login button */
	  	$('#login_button').bind('click', function(e)
	  				{
	  					e.preventDefault();
	  					
	  					self.login();
	  					
	  					return false;
	  				});
	  				
	  	// Bind to logout button
	  	$('#logout_button').bind('click', function(e)
	  				{
	  					e.preventDefault();
	  					
	  					self.logout();
	  					
	  					return false;
	  				});
	  	
	  	if(typeof iJab == undefined) return false;
	  	
	  	var ijabHandler = 
			{
				onEndLogin:function()
				{
					self.hide_login();
				},
				
				onError : function(message)
				{
					self.show_login();
				},
				
				onLogout : function()
				{
					self.show_login();					
				}
			};
			
			iJab.addListener(ijabHandler);
	  },
	  
	  show_login : function()
	  {
	  	$('#logout_button').hide();
	  	
	  	$('#modal').reveal({ 										// The item which will be opened with reveal
							  animation: 'fade',            	    // fade, fadeAndPop, none
								animationspeed: 600,                // how fast animtions are
								closeonbackgroundclick: false,      // if you click background will modal close?
								dismissmodalclass: 'close'    			// the class of a button or element that will close an open modal
							});
	  },
	  
	  hide_login : function()
	  {
	  	$('#logout_button').show();
	  	
	  	$('#modal').trigger('reveal:close');
	  }
}


$(document).ready(function() {
			var im_obj = new IJabIR.IM();
			
			im_obj.show_login();
		});