
angular.module('TemplateDesigner', ['ngDraggable', 'EucaConsoleUtils'])
    .controller('TemplateDesignerCtrl', function($timeout, eucaUnescapeJson) {
        var vm = this;
        //vm.nodes = [{"name":"one", "width":50, "height":50}, {"name":"two", "width":50, "height":50}];
        //vm.links = [{"source":0, "target":1}];
        vm.undoStack = [];
        vm.nodes = [];
        vm.links = [];
        vm.newParam = {};
        vm.initController = function(json_opts, blah) {
            /* html escape */
            json_opts = $('<div/>').html(json_opts).text();
            var opts = JSON.parse(eucaUnescapeJson(json_opts));
            vm.resources = opts.resources;
            vm.setupGraph();
            vm.setData();
        };
        vm.setupGraph = function() {
            vm.force = cola.d3adaptor()
                .linkDistance(90)
                .avoidOverlaps(true)
                .size([800, 600]);
            vm.svg = d3.select("svg")
                .attr("width", 800)
                .attr("height", 600);
        };
        vm.setData = function() {
            // TODO: optimize.. don't remove all here.. leverage enter, update, exit states
            d3.selectAll("svg > *").remove();
            vm.force 
                .nodes(vm.nodes)
                .links(vm.links)
                .start(10, 15, 20);

            var link = vm.svg.selectAll(".link")
                .data(vm.links)
                .enter().append("line")
                .attr("class", "link");

            var color = d3.scale.category20();
            var node = vm.svg.selectAll(".node")
                .enter().append("rect")
                .attr("class", "node")
                .attr("width", function (d) { return d.width; })
                .attr("height", function (d) { return d.height; })
                .attr("rx", 5).attr("ry", 5)
                .style("fill", function (d) { return "#bbbbbb"; })
                .call(vm.force.drag);


            var label = vm.svg.selectAll(".label")
                .enter().append("text")
                .attr("class", "label")
                .attr("text-anchor", "middle")
                .text(function (d) { return d.name; })
                .call(vm.force.drag);

            var menu = vm.svg.selectAll(".menu")
                .enter().append("text")
                .attr("id", function(d) { return "comp-menu"+d.index; })
                .attr("class", "menu")
                .attr("data-dropdown", "designer-action-menu")
                .attr("text-anchor", "right")
                .attr("font-family", "FontAwesome")
                .text(function(d) { return '\uf141'; })
                .on("click", function(evt) {
                    var elem = d3.select(this)[0][0];
                    var idx = parseInt(elem.id.substring(9));
                    var node = vm.nodes[idx];
                    vm.selectedNode = node;
                })
                .call(vm.force.drag);
                $('svg').foundation('dropdown', 'reflow');

            var param = vm.svg.selectAll(".param")
                .enter().append("text")
                .attr("id", function(d) { return "comp-param"+d.index; })
                .attr("class", "param")
                .attr("text-anchor", "right")
                .attr("font-family", "FontAwesome")
                .text(function(d) { return '\uf138'; })
                .on("click", function(evt) {
                    var elem = d3.select(this)[0][0];
                    var idx = parseInt(elem.id.substring(9));
                    var node = vm.nodes[idx];
                })
                .call(vm.force.drag);
                $('svg').foundation('dropdown', 'reflow');

            var output = vm.svg.selectAll(".output")
                .enter().append("text")
                .attr("id", function(d) { return "comp-output"+d.index; })
                .attr("class", "output")
                .attr("text-anchor", "right")
                .attr("font-family", "FontAwesome")
                .text(function(d) { return '\uf138'; })
                .on("click", function(evt) {
                    var elem = d3.select(this)[0][0];
                    var idx = parseInt(elem.id.substring(9));
                    var node = vm.nodes[idx];
                    // save data
                    vm.undoStack.push({"nodes": vm.nodes.slice(0), "links": vm.links.slice(0)});
                    // create temp target for link... so it can be dragged around.
                    vm.nodes.push({"name":"", "width":10, "height":10});
                    vm.links.push({"source": idx, "target": vm.nodes.length-1});
                    vm.setData();
                })
                .call(vm.force.drag);
                $('svg').foundation('dropdown', 'reflow');

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
                menu.attr("x", function (d) { return d.x + 30; })
                     .attr("y", function (d) { return d.y - 30; });
                param.attr("x", function (d) { return d.x - 45; })
                     .attr("y", function (d) { return d.y + 25; });
                output.attr("x", function (d) { return d.x + 30; })
                     .attr("y", function (d) { return d.y + 25; });
            });
        };
        vm.dropComplete = function($data, $event) {
            var pos = $('svg').position();
            var x = $event.x - pos.left;
            var y = $event.y - pos.top;
            // save data
            vm.undoStack.push({"nodes": vm.nodes.slice(0), "links": vm.links.slice(0)});
            var props = $data.properties.slice(0);
            // make copy of each prop obj in array
            angular.forEach(props, function(prop, idx) {
                props[idx] = $.extend(true, {}, prop);
            });
            vm.nodes.push({"name":$data.name, "properties":props, "width":100, "height":100, "x":x, "y":y, "fixed":true});
            vm.setData();
            vm.generateTemplate();
        };
        vm.canUndo = function() {
            return (vm.undoStack.length > 0);
        };
        vm.undoLast = function() {
            if (vm.undoStack.length > 0) {
                var item = vm.undoStack.pop();
                vm.nodes = item.nodes;
                vm.links = item.links;
                vm.setData();
            }
        };
        vm.showPropertiesEditor = function() {
            console.log("node props: "+JSON.stringify(vm.selectedNode.properties));
            $('#property-editor-modal').foundation('reveal', 'open');
        };
        vm.saveProperties = function() {
            angular.forEach(vm.selectedNode.properties, function(prop) {
                prop.value = $("#res-prop-"+prop.name).val();
            });
            $('#property-editor-modal').foundation('reveal', 'close');
        };
        vm.addParameter = function() {
            var paramCount = 0;
            angular.forEach(vm.nodes, function(node) {
                if (node.name == "Parameter") {
                    paramCount = paramCount + 1;
                }
            });
            var x = 60;
            var y = (paramCount * 60) + 35;
            vm.nodes.push({"name":"Parameter", "properties":vm.newParam, "width":100, "height":50, "x":x, "y":y, "fixed":true});
            vm.setData();
            vm.generateTemplate();
            $('#add-parameter-modal').foundation('reveal', 'close');
            vm.newParam = {};
        };
        vm.generateTemplate = function() {
            template = {'AWSTemplateFormatVersion':'2010-09-09'};
            resources = {};
            for (idx in vm.nodes) {
                var node = vm.nodes[idx];
                var name = node.name + '-' + Math.random().toString(36).substring(5)
                resources[name] = {}
                angular.forEach(node.properties, function(prop) {
                    resources[name][prop.name] = prop.value;
                });
            }
            template['Resources'] = resources;
            vm.templateText = JSON.stringify(template, undefined, 2);
        }
    })
