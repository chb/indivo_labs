module("Model: Labs.Models.Lab")

test("findAll", function(){
	stop(2000);
	Labs.Models.Lab.findAll({}, function(labs){
		start()
		ok(labs)
        ok(labs.length)
        ok(labs[0].name)
        ok(labs[0].description)
	});
	
})

test("create", function(){
	stop(2000);
	new Labs.Models.Lab({name: "dry cleaning", description: "take to street corner"}).save(function(lab){
		start();
		ok(lab);
        ok(lab.id);
        equals(lab.name,"dry cleaning")
        lab.destroy()
	})
})
test("update" , function(){
	stop();
	new Labs.Models.Lab({name: "cook dinner", description: "chicken"}).
            save(function(lab){
            	equals(lab.description,"chicken");
        		lab.update({description: "steak"},function(lab){
        			start()
        			equals(lab.description,"steak");
        			lab.destroy();
        		})
            })

});
test("destroy", function(){
	stop(2000);
	new Labs.Models.Lab({name: "mow grass", description: "use riding mower"}).
            destroy(function(lab){
            	start();
            	ok( true ,"Destroy called" )
            })
})