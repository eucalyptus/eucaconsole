
angular.module('TemplateDesigner', ['ngDraggable', 'EucaConsoleUtils'])
    .controller('TemplateDesignerCtrl', function($timeout, eucaUnescapeJson) {
        var vm = this;
        vm.nodes = [{"name":"one", "width":50, "height":50}, {"name":"two", "width":50, "height":50}];
        vm.links = [{"source":0, "target":1}];
        vm.initController = function(json_opts, blah) {
            /* html escape */
            json_opts = $('<div/>').html(json_opts).text();
            var opts = JSON.parse(eucaUnescapeJson(json_opts));
            vm.resources = opts.resources;
            vm.setupGraph();
        };
        vm.setupGraph = function() {
            var color = d3.scale.category20();
            vm.force = cola.d3adaptor()
                .linkDistance(90)
                .avoidOverlaps(true)
                .size([800, 600]);
            vm.svg = d3.select("svg")
                .attr("width", 800)
                .attr("height", 800);
            vm.force 
                .nodes(vm.nodes)
                .links(vm.links)
                .start(10, 15, 20);

            var link = vm.svg.selectAll(".link")
                .data(vm.links)
                .enter().append("line")
                .attr("class", "link");

            var node = vm.svg.selectAll(".node")
                .data(vm.nodes)
                .enter().append("rect")
                .attr("class", "node")
                .attr("width", function (d) { return d.width; })
                .attr("height", function (d) { return d.height; })
                .attr("rx", 5).attr("ry", 5)
                .style("fill", function (d) { return color(1); })
                .call(vm.force.drag);


            var label = vm.svg.selectAll(".label")
                .data(vm.nodes)
                .enter().append("text")
                .attr("class", "label")
                .text(function (d) { return d.name; })
                .call(vm.force.drag);

            node.append("title")
                .text(function (d) { return d.name });

            vm.force.on("tick", function () {
                link.attr("x1", function (d) { return d.source.x; })
                    .attr("y1", function (d) { return d.source.y; })
                    .attr("x2", function (d) { return d.target.x; })
                    .attr("y2", function (d) { return d.target.y; });

                node.attr("x", function (d) { return d.x - d.width / 2; })
                    .attr("y", function (d) { return d.y - d.height / 2; });

                label.attr("x", function (d) { return d.x; })
                     .attr("y", function (d) {
                         var h = this.getBBox().height;
                         return d.y + h/4;
                     });
            });
        }
        vm.dropComplete = function($data, $event) {
            console.log("got drop @"+$event.x+","+$event.y);
            console.log("got data "+$data.name);
            vm.nodes.push({"name":$data.name, "width":50, "height": 50, "x":$event.x, "y":$event.y});
            vm.svg.data(vm.nodes);
        };
    })
