angular.module('ChartServiceModule', [])
.factory('ChartService', function () {
    var margin = {
        top: 15,
        left: 68,
        bottom: 60,
        right: 38
    };
    var timeFormat = '%m/%d %H:%M';

    var svc = {
        renderChart: function (target, results, params) {
            var yFormat = '.0f';
            var thresholdValue;
            params = params || {};

            var chart = nv.models.lineChart()
                .margin(margin)
                .useInteractiveGuideline(true)
                .showYAxis(true)
                .showXAxis(true);

            chart.xScale(d3.time.scale());
            chart.xAxis.tickFormat(function (d) {
                return d3.time.format(timeFormat)(new Date(d));
            });

            // Always use zero baseline
            chart.forceY([0, 10]);

            if(params.unit === 'Percent' || params.metric === 'VolumeIdleTime') {
                chart.forceY([0, 100]);
            }

            // Adjust precision
            if (params.unit === 'Kilobytes') {
                yFormat = '.1f';
            } else if (params.unit === 'Megabytes' || params.unit === 'Gigabytes') {
                yFormat = '.2f';
            }

            if(params.preciseMetrics) {
                yFormat = '.2f';
            }

            if(params.unit === 'Kilobytes') {
                yFormat = '.1f';
            } else if (params.unit === 'Megabytes' || params.unit === 'Gigabytes') {
                yFormat = '.2f';
            }

            if (params.maxValue && params.maxValue < 10 && params.unit !== 'Count') {
                chart.forceY([0, params.maxValue]);
                yFormat = '0.2f';
            }
            if (['VolumeReadBytes', 'VolumeWriteBytes', 'VolumeReadOps', 'VolumeWriteOps'].indexOf(params.metric) !== -1) {
                yFormat = '.1f';
                if (params.maxValue && params.maxValue < 5) {
                    yFormat = '.3f';
                }
            }

            if (params.threshold) {
                // Ensure alarm threshold isn't at the top of the chart when threshold hasn't been exceeded
                thresholdValue = parseInt(params.threshold, 10);
                if (thresholdValue > params.maxValue) {
                    chart.forceY([0, Math.round(thresholdValue + (thresholdValue * 0.25))]);
                }
            }

            chart.yAxis.axisLabel(params.unit).tickFormat(d3.format(yFormat));

            var s = d3.select(target)
                .datum(results)
                .call(chart);

            if (params.noXLabels) {
                svc.moveXAxisLabels(target);
            }

            return chart;
        },

        moveXAxisLabels: function(target) {
            var svg = $(".time-shift svg");
            svg.empty();
            var minMax = d3.select(target).selectAll(".nv-x g.nvd3.nv-wrap.nv-axis .nv-axisMaxMin text");
            var middle = d3.select(target).selectAll(".nv-x g.nvd3.nv-wrap.nv-axis .tick text");
            var labels = minMax[0].slice(0, 2).concat(middle[0]);
            // get translation from parent
            labels.forEach(function(label) {
                var trans = document.createAttribute('transform');
                trans.value = label.parentElement.attributes.transform.value;
                label.attributes.setNamedItem(trans);
            });
            var context = document.createElementNS("http://www.w3.org/2000/svg", "g");
            context.setAttribute("class", "nvd3");
            context.setAttribute("transform", "translate(58,0)");
            context = $(context);
            context.append(labels);
            svg.append(context);
        },

        resetChart: function (target) {
            d3.select(target).selectAll('svg > *').remove();
        }
    };

    return svc;
});
