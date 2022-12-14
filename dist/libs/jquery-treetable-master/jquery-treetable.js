jQuery.fn.extend({
	treetable: function() {
		
		//collection of all the tables selected
		var $tables = $(this);
		var itemsR = [];
		//loop through each table
		for (i = 0; i < $tables.length; i++) {
			var $table = $($tables[i]);	
			//console.log($tables.length);
			//console.log($table);
			//console.log($table.hasClass("tt-table"));
			//console.log($table.is(":visible"));
			//don't paint the tt if the table has already been painted or it's invisible
			if (!$table.hasClass("tt-table") ) {
				$table.addClass("tt-table");
				var $items = $table.find("div.tt");
				var index = {};
				//var itemsR = [];

				// add items to index
				$items.each(function (i, el) {
					var $el = $(el);
					//console.log($el);
					
					var id = $el.data('tt-id');
					var parent = $el.data('tt-parent');
					if(parent === '') {
						parent = undefined;
					}

					var item = {
						id: id,
						parent: parent,
						children: [],
						el: $el,
						left: 0,
						width: $el.width() + 12
					};

					index[id] = item;
					itemsR.push(item);
				});

				// make a graph from parent relations
				itemsR.forEach(function (item) {
					if (item.parent !== undefined) {
						item.parent = index[item.parent];
						item.parent.children.push(item);
					}
				});

				// pad items
				itemsR.forEach(function (item) {

					item.left = 0;
					if (item.parent !== undefined) {
						item.left = item.parent.left + item.parent.width;
					}
				});

				// position items
				itemsR.forEach(function (item) {
					//console.log(el.left);
					item.el.css("left", item.left);
				});

				// wrap contents
				itemsR.forEach(function (item) {
					item.el.html('<div class="content">' + item.el.html() + '</div>');
				});

				// add parent classes
				itemsR.forEach(function (item) {
					if (item.children.length > 0) {
						item.el.addClass("tt-parent");
						item.showChildren = true;
					}
				});


				function drawLines()
				{
					// draw lines
					itemsR.forEach(function (item) {

						if (item.parent === undefined) {
							return;
						}

						var childPos = item.el.position();
						var parent = item.parent;

						var parentPos = parent.el.position();
						var height = childPos.top - parentPos.top;
						var width = item.left - parent.left;
						var left = parent.left - item.left + (parent.width / 2);

						item.el.children('div.tail').first().remove();

						var $tail = $('<div class="tail"></div>').css({
							height: height,
							width: width,
							left: left
						});

						item.el.prepend($tail);
					});
				}
				drawLines();


				// handle click event
				$table.on("click", "div.tt div.content", function (e) {

					var $el = $(e.currentTarget).closest(".tt");
					var $tr = $el.closest("tr");
					var id = $el.data('tt-id');
					var item = index[id];

					if (item.showChildren === true) {
						// hide all children
						item.showChildren = false;

						function hide(parentId) {
							var item = index[parentId];
							item.children.forEach(function (child) {
								if (child.showChildren !== undefined) {
									child.showChildren = false;
								}
								$(child.el).closest("tr").addClass("tt-hide");
								hide(child.id);
							});
						}
						hide(id);
						drawLines();
					} else {
						// show direct children
						item.showChildren = true;
						item.children.forEach(function (child) {
							$(child.el).closest("tr").removeClass("tt-hide");
						});
						drawLines();
					}
				});
			};
		}

		// initially hide all children - we should provide an option to set behavior here
		itemsR.forEach(function (item) {

			if (item.parent === undefined && item.children.length > 0) {
				item.el.find(".content").click();
			}
		});
	}
});

