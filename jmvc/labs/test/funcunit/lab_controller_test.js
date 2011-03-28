module("lab",{
	setup : function(){
		// open the page
		S.open("//labs/labs.html");
		
		//make sure there's at least one lab on the page before running a test
		S('.lab').exists()
	},
	//a helper function that creates a lab
	create : function(){
		S("[name=name]").type("Ice")
	    S("[name=description]").type("Cold Water")
	    S("[type=submit]").click()
		S('.lab:nth-child(2)').exists()
	}
})

test("labs present", function(){
	ok(S('.lab').size() >= 1, "There is at least one lab")
})

test("create labs", function(){
    
	this.create();
	
    S(function(){
		ok(S('.lab:nth-child(2) td:first').text().match(/Ice/), "Typed Ice");
	})
})

test("edit labs", function(){
    this.create();
	
	S('.lab:nth-child(2) a.edit').click();
    S(".lab input[name=name]").type(" Water")
    S(".lab input[name=description]").type("\b\b\b\b\bTap Water")
    S(".update").click()
    S('.lab:nth-child(2) .edit').exists(function(){
		
		ok( S('.lab:nth-child(2) td:first').text().match(/Ice Water/), 
			"Typed Ice Water");
		 
		ok( S('.lab:nth-child(2) td:nth-child(2)').text().match(/Cold Tap Water/), 
			"Typed Cold Tap Water");
	})

})


test("destroy", function(){
	this.create();

    S(".lab:nth-child(2) .destroy").click();
	
	//makes the next confirmation return true
    S.confirm(true);
	
	S('.lab:nth-child(2)').missing(function(){
		ok("destroyed");
	})
    
	
});