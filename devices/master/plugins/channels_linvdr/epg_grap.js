/* 

curl -s "http-URL.ts"  | nodejs epg_grap.js 1

reads ts stream from stdin, read epg data and stops after n repeats of the same time stamp.
The received epg data is dumped as json string to stdout
*/

var dvbtee = require('dvbtee')
var fs = require('fs')

var rs = null
var parser = new dvbtee.Parser

var result = { 'service_ids': new Object(), 'details': new Object() }

var details = result.details
var nrOfLoops=parseInt(process.argv[2])

parser.on('data', function (data) {
	//console.log("table name ",data.tableName)
	if (data.tableName == "SDT") {
		/*
				console.log(
				'table id: ' + data.tableId,
				'\ntable name: ' + data.tableName,
				'\ntable data:\n', JSON.stringify(data, null, 2)
				)
		*/
		if (data.services) {
			data.services.forEach(function (service) {
				var serviceId = service.serviceId
				if (service.descriptors) {
					service.descriptors.forEach(function (descriptor) {
						if (descriptor.descriptorTag == 72) {
							var serviceName = descriptor.serviceName
							//var providerName = descriptor.providerName
							//console.log(serviceId, providerName,serviceName)
							result.service_ids[serviceId] = serviceName
						}
					})
				}
			})
		}
	}
	if (data.tableName == "EIT") {
		/*
				var serviceId=data.serviceId
				console.log(
					'serviceId id: ' + data.serviceId,
					'\ntable name: ' + data.tableName,
					'\ntable data:\n', JSON.stringify(data, null, 2)
				)
		*/
		if (data.events) {
			data.events.forEach(function (item) {
				var name = ''
				var title = ''
				var description = ''
				starttime = item.unixTimeBegin
				endtime = item.unixTimeEnd
				eventId = item.eventId
				//console.log(JSON.stringify( item, null, 2))
				if (item.descriptors) {
					item.descriptors.forEach(function (descriptor) {
						//console.log(JSON.stringify( descriptor, null, 2))
						if (descriptor.descriptorTag == 77) {
							name = descriptor.name
							title = descriptor.text
						}
						if (descriptor.descriptorTag == 78) {
							description += descriptor.text.replace(/[\u008A]/g,'\n')
						}
					})
				}
				var key = data.serviceId.toString() + ':' + item.unixTimeBegin.toString()
				if (details[key]) {
					details[key].counter++;
					//console.log('Double try..', title, name,details[key].counter)
					if (details[key].counter > nrOfLoops) {
						//console.log('Double - try to break..',title)
						//console.log(JSON.stringify(result, replacer, 2))
						console.log(JSON.stringify(result, null, 2))
						rs.destroy()

					}
				} else {
					details[key] =
					{
						'name': name,
						'counter': 1,
						'title': title,
						'description': description,
						'unixTimeBegin': item.unixTimeBegin,
						'unixTimeEnd': item.unixTimeEnd
					}
				}
				/*				console.log(
									'name: ' + name,
									'\ntitle: ' + title,
									'\nstarttime: ' + starttime,
									'serviceId: ' + serviceId,
									'provider:' + result.service_ids[serviceId],
									'\nendtime: ' + endtime,
									'\ndescription:\n' + description,
								)
				*/
			})
		}

	}
})
parser.on('end', function () {})

rs = process.stdin
//rs.on('error', function(err) {console.log(err)}); // Handle the error
//rs.on('end', function(){})
rs.pipe(parser, { end: false })
