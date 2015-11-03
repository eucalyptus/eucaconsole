
angular.module('TemplateDesigner', ['ngDraggable', 'EucaConsoleUtils'])
    .controller('TemplateDesignerCtrl', function($http, $timeout, eucaUnescapeJson, eucaHandleError) {
        var vm = this;
        vm.undoStack = [];
        vm.nodes = [];
        vm.links = [];
        vm.newParam = {'datatype':'String'}; // sane default
        vm.connectingFrom = undefined;
        vm.connectTo = undefined;
        vm.initController = function(json_opts, blah) {
            /* html escape */
            json_opts = $('<div/>').html(json_opts).text();
            var opts = JSON.parse(eucaUnescapeJson(json_opts));
            vm.resources = opts.resources;
            vm.setupGraph();
            vm.setupListeners();
            // add initial param for testing
            var x = 60;
            var y = 35;
            vm.nodes.push({"name":"Parameter", "properties":{"name":"ImageID", "datatype":"AWS::EC2::Image::Id"}, "width":100, "height":50, "x":x, "y":y, "fixed":true});
            y = 95;
            vm.nodes.push({"name":"Parameter", "properties":{"name":"KeyName", "datatype":"AWS::EC2::KeyPair::KeyName"}, "width":100, "height":50, "x":x, "y":y, "fixed":true});
            vm.setData();
            jQuery.fn.d3Click = function () {
              this.each(function (i, e) {
                var evt = document.createEvent("MouseEvents");
                evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);

                e.dispatchEvent(evt);
              });
            };
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

            var node = vm.svg.selectAll(".node")
                .data(vm.nodes)
                .enter().append("rect")
                .attr("class", "node")
                .attr("width", function (d) { return d.width; })
                .attr("height", function (d) { return d.height; })
                .attr("rx", 5).attr("ry", 5)
                .style("fill", function (d) { return "#bbbbbb"; })
                .on("click", function(node, idx) {
                    if (vm.connectingFrom !== undefined) {
                        if (vm.nodes[vm.connectingFrom].name === "Parameter") {
                            // prompt for property to set
                            $('#param-connect-modal').foundation('reveal', 'open');
                            $timeout(function() {
                                vm.connectTo = idx;
                            });
                        }
                        // else it's another node, so case-by-case basis
                    }
                })
                .call(vm.force.drag);


            var label = vm.svg.selectAll(".label")
                .data(vm.nodes)
                .enter().append("text")
                .attr("class", "label")
                .attr("text-anchor", "middle")
                .text(function (d) {
                    if (d.name == "Parameter") {
                        return d.properties.name;
                    }
                    return d.name;
                })
                .call(vm.force.drag);

            var menu = vm.svg.selectAll(".menu")
                .data(vm.nodes)
                .enter().append("text")
                .attr("id", function(d) { return "comp-menu"+d.index; })
                .attr("class", "menu")
                .attr("data-dropdown", "designer-action-menu")
                .attr("text-anchor", "right")
                .attr("font-family", "FontAwesome")
                .text(function(d) { return '\uf141'; })
                .on("click", function(node) {
                    vm.selectedNode = node;
                });
            $('svg').foundation('dropdown', 'reflow');

            var output = vm.svg.selectAll(".output")
                .data(vm.nodes)
                .enter().append("text")
                .attr("id", function(d) { return "comp-output"+d.index; })
                .attr("class", "output")
                .attr("text-anchor", "right")
                .attr("font-family", "FontAwesome")
                .text(function(d) { return '\uf138'; })
                .on("mousedown", function(node, idx) {
                    var x = node.x + 50;
                    var y = node.y + ((node.name=="Parameter")?12:35);
                    vm.svg.append("line")
                    .attr("class", "connecting")
                    .attr("stroke-dasharray", "5 5")
                    .attr("x1", x)
                    .attr("y1", y)
                    .attr("x2", x+10)
                    .attr("y2", y);
                    vm.connectingFrom = idx;
                });

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
                     .attr("y", function (d) { return d.y - ((d.height==100)?30:10); });
                output.attr("x", function (d) { return d.x + 30; })
                     .attr("y", function (d) { return d.y + ((d.height==100)?42:17); });
            });
        };
        vm.setupListeners = function() {
            vm.svg.on("keypress", function($event) {
                var key = $event.which || $event.keyCode || $event.charCode;
                if (key === 27) {
                    vm.svg.select('.connecting').remove();
                }
            });
            vm.svg.on("mousemove", function() {
                if (vm.connectingFrom !== undefined) {
                    var coords = d3.mouse(this);
                    $('.connecting').attr('x2', coords[0]).attr('y2', coords[1]);
                }
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
            vm.nodes.push({"name":$data.name, cfn_type:$data.cfn_type, "properties":props, "width":100, "height":100, "x":x, "y":y, "fixed":true});
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
        vm.linkParameter = function(prop) {
            $('#param-connect-modal').foundation('reveal', 'close');
            prop.value = {"Ref":vm.nodes[vm.connectingFrom].properties.name};
            vm.undoStack.push({"nodes": vm.nodes.slice(0), "links": vm.links.slice(0)});
            vm.links.push({"source":vm.connectingFrom, "target":vm.connectTo});
            vm.connectingFrom = undefined;
            vm.connectTo = undefined;
            vm.setData();
            vm.generateTemplate();
        };
        vm.showPropertiesEditor = function() {
            // trigger fetch(es) to populate selects as needed
            angular.forEach(vm.selectedNode.properties, function(prop) {
                if (prop.data === undefined && prop.data_url !== undefined) {
                    var data = "csrf_token="+$('#csrf_token').val();
                    $http({method:'POST', url:prop.data_url, data:data,
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                    success(function(oData) {
                        var results = oData ? oData.results : [];
                        prop.data = vm.resultsToOptions(results);
                    }).
                    error(function (oData, status) {
                        eucaHandleError(oData, status);
                    });
                }
            });
                
            $('#property-editor-modal').foundation('reveal', 'open');
        };
        vm.isPropertyARef = function(prop) {
            return (typeof prop.value) !== "string" && prop.value !== undefined && prop.value.Ref !== undefined;
        };
        vm.resultsToOptions = function(items) {
            var ret = [];
            var i;
            angular.forEach(items, function(item) {
                var name = item.id;
                if (item.name !== undefined) {
                    name = item.name;
                }
                this.push([item.id, name]); 
            }, ret);
            return ret;
        };
        vm.saveProperties = function() {
            angular.forEach(vm.selectedNode.properties, function(prop) {
                if (!vm.isPropertyARef(prop)) {
                    prop.value = $("#res-prop-"+prop.name).val();
                }
            });
            $('#property-editor-modal').foundation('reveal', 'close');
            vm.generateTemplate();
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
            vm.newParam = {'datatype':'String'}; // sane default
        };
        vm.generateTemplate = function() {
            template = {'AWSTemplateFormatVersion':'2010-09-09'};
            properties = {};
            resources = {};
            for (var idx in vm.nodes) {
                var node = vm.nodes[idx];
                var name;
                if (node.name == "Parameter") {
                    name = node.properties.name;
                    properties[name] = {
                        "Description":node.properties.description,
                        "Type":node.properties.datatype,
                        "Default":node.properties.default
                    };
                }
                else {
                    name = node.name + Math.random().toString(36).substring(5);
                    props = {};
                    angular.forEach(node.properties, function(prop) {
                        if (prop.required === true || (prop.value !== undefined && prop.value !== '')) {
                            props[prop.name] = prop.value;
                        }
                    });
                    resources[name] = {
                        "Type": node.cfn_type,
                        "Properties": props
                    };
                }
            }
            if (Object.keys(properties).length > 0) {
                template.Parameters = properties;
            }
            template.Resources = resources;
            vm.templateText = JSON.stringify(template, undefined, 2);
        };
    });
