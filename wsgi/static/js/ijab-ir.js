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
        
        this.bind_events();
    },
    
    /*
     * Properties
     */
    baseURL							: "",

		/*
		 * Functions
		 */
		add_friends : function(friends)
		{
			/* <div class="ijab-contactview-item ijab-contactview-item-normal" id="ijabuser_victor.hashpar@gmail.com" title="Victor Hashpar&lt;victor.hashpar@gmail.com&gt;"><div class="statusicon"> <img src="http://flask-ijab.rhcloud.com/ijab_im/ijab/images/status/available.png"> </div> <div class="names names_nostatus" title="Victor Hashpar&lt;victor.hashpar@gmail.com&gt;"> <span>Victor Hashpar</span><input type="text" tabindex="0" class="ijab-contactview-item-editor" style="display: none;"><br> <span class="ijab-gray"></span> </div> </div>
			*/
			$("#chat-content").empty();
			
			var len_f = friends.length;
			for(var i = 0; i < len_f && i < 5; ++i)
			{
				var div_jid = 'ijabuser_' + friends[i].jid;
				var div_title = friends[i].name + '&lt;' + friends[i].jid + '&gt';
				
				var img_src = 'http://flask-ijab.rhcloud.com/ijab_im/ijab/images/status/available.png';
				$('div.ijab-contactview-item').each(function(index)
										{
											if($(this).attr('id').indexOf(friends[i].jid) >= 0)
											{
												img_src = $(this).find('img').attr('src');
												return;
											}											
										});
				
				
				var f_html = '<div class="ijab-contactview-item ijab-contactview-item-normal" ';
					  f_html += 'onclick="iJab.talkTo(\'' + friends[i].jid + '\')" ';
					  f_html += 'id="' + div_jid + '" title="' + div_title + '">';
					  f_html += '<div class="statusicon"> <img src="' + img_src + '"> </div> <div class="names names_nostatus" title="' + div_title + '"> <span>' + friends[i].name + '</span><input type="text" tabindex="0" class="ijab-contactview-item-editor" style="display: none;"><br> <span class="ijab-gray"></span> </div> </div>';
					  
				$("#chat-content").append(f_html);
			}
		},
		
		set_user_type : function(user_type)
		{
			$("#cse_gplus_title").text("Search with Google+ -- Guessing Your Professional Area: " + user_type.type);
		},
		
		bind_events : function()
		{
			var self = this;
			// Set autocmoplete
			$("#query_terms").autocomplete({
			      source: function(request, response){
			      		var parent_self = self;
			      		$.getJSON( "/suggestions", {
            								term: $("#query_terms").val()
          									}, function(data)
		          									{
		          										response(data.suggestions);
		          										parent_self.add_friends(data.friends);
		          										parent_self.set_user_type(data.usertype);
		          									}
          							);
          					},
			      minLength: 2,
			      select: function( event, ui ) {
			        //log( ui.item ?
			        //  "Selected: " + ui.item.value + " aka " + ui.item.id :
			        //  "Nothing selected, input was " + this.value );
      				}
    		});
    		
    	// Make friendes list window floating and draggable
    	$("#chat-helper-widget").draggable();
    	
    	// Bind to search button
    	$("#search_button").bind('click', function(e){
    																				e.preventDefault();
    																				self.do_search();
    																				return false;
    																		});
    																		
    	// Bind to clear search result button
    	$("#clear_button").bind('click', function(e){
    																				e.preventDefault();
    																				self.clear_search_result();
    																				return false;
    																		});
		},
		
		do_search : function()
		{
			$('#search_result').show();
			var url = encodeURIComponent('http://www.google.com/search');			
			var query_string = encodeURIComponent('hl=en&q=' + $("#query_terms").val());
			$('#search_result').load('/search?url=' + url + '&query_string=' + query_string, 
															function(){
																$('#wrapper').height(120);
																$('#logo').hide();
																$('#clear_button').show();
															});
		},
		
		clear_search_result : function()
		{
			$('#search_result').hide();
			$('#search_result').empty();
			
			$('#wrapper').height('60%');
			$('#logo').show();
			$('#clear_button').hide();
		}
});

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
        
        this.bind_events();
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
	  	if(typeof iJab == "undefined") return false;
	  	
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
	  	if(typeof iJab == "undefined") return false;
	  	
	  	iJab.logout();
	  },
	  
	  g_oauth : function()
	  {
	  	var ep = 'https://accounts.google.com/o/oauth2/auth';
	  	
	  	// Scopoe
	  	var scope = 'https://www.googleapis.com/auth/plus.login';
	  	
	  	// state
	  	var state = 'ijab';
	  	
	  	// redirect URL
	  	var redirect_uri = 'http://flask-ijab.rhcloud.com/oauth2callback';
	  	
	  	// response type
	  	var response_type = 'code';
	  	
	  	// access type
	  	var access_type = 'offline';
	  	
	  	// client id
	  	var client_id = '504754513196-kk98ot5v9ch3tbqsrat55o76gf8gaa9m.apps.googleusercontent.com';
	  	
	  	var url = ep + '?scope=' + encodeURIComponent(scope);
	  		  url += '&state=' + encodeURIComponent(state);
	  		  url += '&redirect_uri=' + encodeURIComponent(redirect_uri);
	  		  url += '&response_type=' + response_type;
	  		  url += '&access_type=' + access_type;
	  		  url += '&client_id=' + client_id;
	  	
	  	//var pop_w = window.open(url, 'Google OAuth', 'width=300,height=400');
	  	$('#login_button').attr('href', url);
	  },
	  
	  bind_events : function()
	  {
	  	var self = this;
	  	
	  	self.g_oauth();
	  	
	  	/* Bind to login button */
	  	$('#login_button').bind('click', function(e)
	  				{
	  					//e.preventDefault();
	  					
	  					self.login();
	  					
	  					//return false;
	  				});
	  				
	  	// Bind to logout button
	  	$('#logout_button').bind('click', function(e)
	  				{
	  					e.preventDefault();
	  					
	  					self.logout();
	  					
	  					return false;
	  				});
	  	
	  	var ijabHandler = 
			{
				onEndLogin:function()
				{
					self.hide_login();
					
					var userName = document.getElementById("login").value;
					var password = document.getElementById("password").value;
					self.g_oauth();
				},
				
				onResume:function()
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
			
			var attach_ijab_listener = function()
							{
								if(typeof iJab == "undefined")
								{
									setTimeout(attach_ijab_listener, 1000);
									return false;
								}	
								else
								{
									iJab.addListener(ijabHandler);
								}
							};
			attach_ijab_listener();			
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
});


$(document).ready(function() {
			var im_obj = new IJabIR.IM();
			
			im_obj.show_login();
			
			var search_obj = new IJabIR.Search();
		});