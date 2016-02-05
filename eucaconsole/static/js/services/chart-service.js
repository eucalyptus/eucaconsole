angular.module('ChartServiceModule', [])
.factory('ChartService', function () {
    var margin = {
        left: 68,
        right: 38
    };
    var timeFormat = '%m/%d %H:%M';

    return {
        renderChart: function (target, results, params) {
            var yFormat = '.0f';
            params = params || {};
            if(!params.alarms) {
                params.alarms = [];
            }

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

            chart.yAxis.axisLabel(params.unit).tickFormat(d3.format(yFormat));

            var s = d3.select(target)
                .datum(results)
                .call(chart);

            var alarmLines = s.select('.nv-lineChart > g')
                .append('g').attr('class', 'euca-alarmLines')
                .datum(function () {
                    return params.alarms.map(function (current) {
                        return current.threshold;
                    });
                })
                .call(function (selection) {
                    this.datum().forEach(function (threshold) {
                        if(params.unit === 'Percent') {
                            threshold = threshold * 100;
                        }
                        var y = chart.yScale()(threshold),
                            xDomain = chart.xScale().domain(),
                            xEnd = chart.xScale()(xDomain[1]);

                        selection.append('line')
                            .attr('class', 'alarm')
                            .attr('threshold', threshold)
                            .attr('x1', 0)
                            .attr('y1', y)
                            .attr('x2', xEnd)
                            .attr('y2', y);
                    });
                });

            return chart;
        },

        resetChart: function (target) {
            d3.select(target).selectAll('svg > *').remove();
        }
    };
});
