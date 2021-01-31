// dashboard control
if (/dashboard.*/.test(window.location.pathname)) {
  document.addEventListener('DOMContentLoaded', () => {
    fetch(`/get_dashboard_info`)
      .then(response => response.json())
      .then(fill_dashboard)
      .then(show_dashboard)
      .then(addPendingClickEvent)
  })
}

function show_dashboard(input_) {
  document.querySelector("#dashboardLoadingGroup").hidden = false;
  document.querySelector("#dashboardLoadingLabel").hidden = true;
  return input_;
}

function fill_dashboard(input_) {
  if (input_.auth_level === 1) {
    document.querySelector('#numEngines').textContent = input_.engine_count;
    document.querySelector('#numTypes').textContent = input_.type_count;
    document.querySelector('#numSites').textContent = input_.site_count;
    document.querySelector('#numCustomers').textContent = input_.customer_count;
    document.querySelector('#numInService').textContent = input_.service_count;
    document.querySelector('#numRepairing').textContent = input_.repairing_count;
    document.querySelector('#numInTransit').textContent = input_.transit_count;
    document.querySelector('#numRD').textContent = input_.RD_count;
    let tableBody = document.querySelector('#dashboardPendingBody');
    tableBody.innerHTML = ''
    for (engine of input_.pending_engines) {
      tableBody.insertAdjacentHTML('beforeend',
      `
      <tr class='dashboardPendingRows d-flex'>
      <th scope="row" class="col-2" id="pendingSN">${engine.eng_sn}</th>
      <td class="col-1" id="pendingSites">${engine.site_id}</td>
      <td class="col-1" id="pendingSites">${engine.maint_log_id}</td>
      <td class="col-3" id="pendingStatus">${engine.maint_status}</td>
      <td class="col-2" id="pendingStartDate">${engine.in_date}</td>
      <td class="col-3" id="pendingStartDate">${engine.owner_name} (${engine.owner_id})</td>
      </tr>    
      `)
    }
    siteTurnaroundTimeChart(input_);
    engineCountChart(input_);

  } else {
    document.querySelector('#site-name').textContent = input_.site_id;
    document.querySelector('#numEngines').textContent = input_.engine_count;
    document.querySelector('#numOnSites').textContent = input_.on_site_count;
    document.querySelector('#numInTransit').textContent = input_.transit_count;
    let tableBody = document.querySelector('#dashboardPendingBody');
    tableBody.innerHTML = ''
    for (engine of input_.pending_engines) {
      tableBody.insertAdjacentHTML('beforeend',
      `
      <tr class='dashboardPendingRows d-flex'>
      <th scope="row" class="col-2" id="pendingSN">${engine.eng_sn}</th>
      <td class="col-1" id="pendingSites">${engine.maint_log_id}</td>
      <td class="col-3" id="pendingStatus">${engine.maint_status}</td>
      <td class="col-3" id="pendingStartDate">${engine.in_date}</td>
      <td class="col-3" id="pendingStartDate">${engine.owner_name} (${engine.owner_id})</td>
      </tr>    
      `)
    }
    
  }

  return input_;
}

function addPendingClickEvent(input_) {
  const rows = document.querySelectorAll('.dashboardPendingRows');
  rows.forEach(row => {
    row.addEventListener("click", () => {
      console.log(input_)
      let logID = 0;
      if (input_.auth_level === 1) {
        logID = row.children[2].textContent;
        console.log(logID)
      } else {
        logID = row.children[1].textContent;
      }
      window.location.href = `${window.location.origin}/search?q=${logID}`
    })
  })
  return input_
}

//dashboard chart - turnaround time
function siteTurnaroundTimeChart(input_) {
  let ctx = document.getElementById('TATchart').getContext('2d');
  let siteLabel = [];
  let siteData = [];
  for (data of input_.TAT_list) {
    siteLabel.push(data.site_id);
    siteData.push(data.TAT);
  }
  let TATchart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: siteLabel,
        datasets: [{
            label: 'Average Turnaround Time (Days)',
            data: siteData,
            backgroundColor: [
                '#56afbd',
                '#56afbd',
                '#56afbd',
            ],
            borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(54, 162, 235, 1)',
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    fontColor: 'white'
                },
                // gridLines: {
                //   color: "#FFFFFF"
                // }

            }],
            xAxes: [{
              ticks: {
                  fontColor: 'white'
              }
          }],


        },
        legend: {
          labels: {
              // This more specific font property overrides the global property
              fontColor: 'white'
          }
      }
    }
});
}

// dashboard chart - total engines
function engineCountChart(input_) {
  let ctx = document.getElementById('totalEngineChart').getContext('2d');
  let siteLabel = [];
  let siteData = [];
  for (data of input_.TAT_list) {
    siteLabel.push(data.site_id);
    siteData.push(data.TAT);
  }

  engineChartDataDict = {
    datasets: [{
        data: [input_.service_count, input_.repairing_count, 
               input_.RD_count, input_.transit_count],
        backgroundColor: [
          '#56afbd',
          '#d99477',
          '#ebe854',
          '#88f07a'
        ],
    }],

    // These labels appear in the legend and in the tooltips when hovering different arcs
    labels: [
        '# In Service',
        '# Repairing',
        '# R&D',
        '# In transit'
    ]
};

engineChartOptions = {
  elements: {
    center: {
      text: `#Engines: ${input_.engine_count}`,
      color: 'white', // Default is #000000
      fontStyle: 'Arial', // Default is Arial
      sidePadding: 20, // Default is 20 (as a percentage)
      minFontSize: 10, // Default is 20 (in px), set to false and text will not wrap.
      lineHeight: 10 // Default is 25 (in px), used for when text wraps
    }
  },
  legend: {
    labels: {
        // This more specific font property overrides the global property
        fontColor: 'white'
    },
    position: 'left'
}
}

let countChart = new Chart(ctx, {
  type: 'doughnut',
  data: engineChartDataDict,
  options: engineChartOptions
});
}

// for engine_list page
if (/engine_list.*/.test(window.location.pathname) && 
    !/.*search_result.*/.test(window.location.pathname)) {
  document.querySelector("#engineListSummaryDiv").hidden = false;
  document.querySelector("#engineInfoDiv").hidden = false;

  let listOptions = document.querySelector('#listOptions');
  listOptions.addEventListener('click', (event) => {
    const isInput = event.target.nodeName === 'INPUT';
    if (!isInput) {
      return;
    }
    let isInService = 
      document.querySelector('#inServiceCheckBox').checked ? 1 : 0;
    let isMaintenance = 
      document.querySelector('#maintenanceCheckBox').checked ? 1 : 0;
    let isOthers = 
      document.querySelector('#othersCheckBox').checked ? 1 : 0;
    let current_url = window.location.href;
    window.location.href = current_url.replace(/engine_list.*/,
      `engine_list/${isInService}${isMaintenance}${isOthers}`);
  })
  

  document.addEventListener("DOMContentLoaded", () => {
    const rows = document.querySelectorAll('.engineSummaryRows');
    
    rows.forEach(row => {
      row.addEventListener("click", () => {
        let eng_sn = row.children[0].textContent;
        fetch(`/get_engine_info/${eng_sn}`)
          .then(response => response.json()) 
          .then(fillEngineInfoTable)
      })
    })
  })
};

function fillEngineInfoTable(jsonInput) {
  document.querySelector('#engineInfoDiv').hidden = false;
  document.querySelector('#cell_eng_sn').textContent = jsonInput.eng_sn;
  document.querySelector('#cell_eng_pn').textContent = jsonInput.eng_pn;
  document.querySelector('#cell_customer').textContent = jsonInput.customer;
  document.querySelector('#cell_maint_site').textContent = jsonInput.maint_site;
  document.querySelector('#cell_build_date').textContent = jsonInput.build_date;
  document.querySelector('#cell_op_hrs').textContent = jsonInput.op_hrs;
  document.querySelector('#cell_cycle').textContent = jsonInput.cycle;
  document.querySelector('#cell_engine_status').textContent = jsonInput.engine_status;
  document.querySelector('#cell_maint_log_id').textContent = jsonInput.maint_log_id;
  document.querySelector('#cell_maint_status').textContent = jsonInput.maint_status;
  document.querySelector('#engineListSNLabel').textContent = jsonInput.eng_sn;

}

// search by engine S/N
if (/.*search_result.*/.test(window.location.pathname)) {
  const eng_sn = window.location.pathname.replace("/engine_list/search_result_","");
  fetch(`/get_engine_info/${eng_sn}`)
  .then(response => response.json()) 
  .then(fillEngineInfoTable)
  .then(()=>{document.querySelector("#engineInfoDiv").hidden = false;})
}

// for sites page
if (/site_list.*/.test(window.location.pathname) &&
    !/.*search_result_.*/.test(window.location.pathname)) {
  document.addEventListener("DOMContentLoaded", ()=> {
    const rows = document.querySelectorAll('.siteSummaryRows');
    rows.forEach(addSiteRowsEvent)
      })
} else if (/.*search_result_.*/.test(window.location.pathname)) {
  const site_id = window.location.pathname.replace("/site_list/search_result_","");
  console.log(site_id)
  fetchSiteEngineInfo(site_id);
}

function addSiteRowsEvent(row) {
  row.addEventListener("click", () => {
    let site_id = row.children[0].textContent;
    fetchSiteEngineInfo(site_id);
  })
}

async function fetchSiteEngineInfo(site_id) {
  await fetch(`/get_site_engine_info/${site_id}`)
  .then(response => response.json())
  .then(insertSiteEngineData);
  document.querySelector('#siteLabel').textContent = site_id; // reason for making the fetch async
}

function insertSiteEngineData(results) {
  let tableBody = document.querySelector('#siteEngineDataBody');
  tableBody.innerHTML = ''
  if (results.length == 0) {
    tableBody.insertAdjacentHTML('beforeend',
    `
    <tr class='siteEngineDataRows d-flex'>
    <th scope="row" class="col-3">(No engine on this site)</th>
    <td></td>
    <td></td>
    <td></td>
    </tr>
    `
    );
  } else {
    for (result of results) {
      tableBody.insertAdjacentHTML('beforeend',
      `
      <tr class='siteEngineDataRows d-flex'>
      <th scope="row" class="col-3">${result.eng_sn}</th>
      <td class="col-2">${result.eng_pn}</td>
      <td class="col-3">${result.in_date}</td>
      <td class="col-4">${result.maint_status}</td>
      </tr>
      `
      );
    }
  }
}

// Maint. Log check botton control
if (/maint_log_list.*/.test(window.location.pathname)) {
  document.addEventListener('DOMContentLoaded', generateMaintLog.bind(fillMaintLog))
  checkbox = document.querySelector("#activeCaseOnly");
  checkbox.addEventListener('change', generateMaintLog.bind(fillMaintLog))

}

function generateMaintLog() {
    let isActiveOnly = checkbox.checked ? 1 : 0;
    fetch(`/get_main_log_list_info/${isActiveOnly}`)
      .then(response => response.json())
      .then(this) // The .bind function will make 'this' the provided argument.
      
}

function fillMaintLog(result) {
  let tableBody = document.querySelector('#maintLogListBody');
  tableBody.innerHTML = '';
  trID = 0;
  for (data of result) {
    tableBody.insertAdjacentHTML('beforeend',
    `
    <tr class='logSummaryRows' id='${trID}'>
    <th scope="row" class="sticky-col">${data.maint_log_id}</th>
    <td class="sticky-col">${data.eng_sn}</td>
    <td>${data.maint_site_id}</td>
    <td>${data.maint_type}</td>
    <td>${data.maint_status}</td>
    <td>${data.note}</td>
    </tr>
    `
    );
    trID++;
  }
  const rows = document.querySelectorAll('.logSummaryRows');
  rows.forEach(row => {
    row.addEventListener("click", (e) => {
      let index = parseInt(e.target.parentElement.id);
      let detailBody = document.querySelector('#maintLogDetailBody');
      let emailBody = document.querySelector('#emailBody');
      detailBody.innerHTML = '';
      emailBody.innerHTML = '';
      let label = document.querySelector('#maint-log-detail-label')
      label.textContent = `Log ID ${result[index].maint_log_id}, Engine S/N ${result[index].eng_sn}`
      detailBody.insertAdjacentHTML('beforeend',
          `
          <tr class='logDetailRow'>
          <td>${result[index].in_date}</td>
          <td>${result[index].out_date}</td>
          <td>${result[index].maint_cost}</td>
          <td>${result[index].owner_name} (${result[index].owner_id})</td>
          </tr>
          `
          );
      emailBody.insertAdjacentHTML('beforeend', 
        `
          <td>${result[index].owner_email}</td>
        `
      );
    })
  })

}


// put text at the center of the pie chart

Chart.pluginService.register({
  beforeDraw: function(chart) {
    if (chart.config.options.elements.center) {
      // Get ctx from string
      var ctx = chart.chart.ctx;

      // Get options from the center object in options
      var centerConfig = chart.config.options.elements.center;
      var fontStyle = centerConfig.fontStyle || 'Arial';
      var txt = centerConfig.text;
      var color = centerConfig.color || '#000';
      var maxFontSize = centerConfig.maxFontSize || 75;
      var sidePadding = centerConfig.sidePadding || 20;
      var sidePaddingCalculated = (sidePadding / 100) * (chart.innerRadius * 2)
      // Start with a base font of 30px
      ctx.font = "30px " + fontStyle;

      // Get the width of the string and also the width of the element minus 10 to give it 5px side padding
      var stringWidth = ctx.measureText(txt).width;
      var elementWidth = (chart.innerRadius * 2) - sidePaddingCalculated;

      // Find out how much the font can grow in width.
      var widthRatio = elementWidth / stringWidth;
      var newFontSize = Math.floor(30 * widthRatio);
      var elementHeight = (chart.innerRadius * 2);

      // Pick a new font size so it will not be larger than the height of label.
      var fontSizeToUse = Math.min(newFontSize, elementHeight, maxFontSize);
      var minFontSize = centerConfig.minFontSize;
      var lineHeight = centerConfig.lineHeight || 25;
      var wrapText = false;

      if (minFontSize === undefined) {
        minFontSize = 20;
      }

      if (minFontSize && fontSizeToUse < minFontSize) {
        fontSizeToUse = minFontSize;
        wrapText = true;
      }

      // Set font settings to draw it correctly.
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      var centerX = ((chart.chartArea.left + chart.chartArea.right) / 2);
      var centerY = ((chart.chartArea.top + chart.chartArea.bottom) / 2);
      ctx.font = fontSizeToUse + "px " + fontStyle;
      ctx.fillStyle = color;

      if (!wrapText) {
        ctx.fillText(txt, centerX, centerY);
        return;
      }

      var words = txt.split(' ');
      var line = '';
      var lines = [];

      // Break words up into multiple lines if necessary
      for (var n = 0; n < words.length; n++) {
        var testLine = line + words[n] + ' ';
        var metrics = ctx.measureText(testLine);
        var testWidth = metrics.width;
        if (testWidth > elementWidth && n > 0) {
          lines.push(line);
          line = words[n] + ' ';
        } else {
          line = testLine;
        }
      }

      // Move the center up depending on line height and number of lines
      centerY -= (lines.length / 2) * lineHeight;

      for (var n = 0; n < lines.length; n++) {
        ctx.fillText(lines[n], centerX, centerY);
        centerY += lineHeight;
      }
      //Draw text in center
      ctx.fillText(line, centerX, centerY);
    }
  }
});