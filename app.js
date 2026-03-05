

let dataArray = [];
let assetFocus = null;

const fieldNames = [
        "stockName", "assetId", "valueNis", "portfolioPrecentage", "nShares", "changePrecent", "price", "precentBuy", "type", "warning", "buy", "coin", "conv", "market", "dDailyNis", "dailyPrecent"
    ];
const fieldDisplayNames = [
        "Name", "Id", "Value", "% of", "Shares", "Change %", "Price", "precentBuy", "type", "warning", "buy", "coin", "conv", "Market", "dDailyNis", "dailyPrecent"
    ];
function fixFloat(d) {
    if (typeof d === "string" && d.length == 0) {
        return d;
    }   
    return parseFloat(d).toFixed(4);
}
function convD(i, d) {
    switch(i) {
        case 3: return fixFloat(d);
        case 5: return fixFloat(d);
        case 7: return fixFloat(d);
        case 12: return fixFloat(d);
        case 13: return d.substring(0, 5);
        case 15: return fixFloat(d);
    }
    return d;   
}

function getNextStock(add) {
    if (!assetFocus) return;
    const lastItem = dataArray[0];
    const currentIndex = lastItem.data.findIndex(r => r.assetId === assetFocus);
    if (currentIndex === -1) return;
    const nextIndex = currentIndex + add;
    if (nextIndex < 0 || nextIndex >= lastItem.data.length) return;
    const nextAssetId = lastItem.data[nextIndex].assetId;
    trackStock(nextAssetId);
}
function trackStock(assetId) {
    console.log("Tracking asset:", assetId);
    assetFocus = assetId;
    const chart = [];
    dataArray.map(item => {
        const row = item.data.find(r => r.assetId === assetId);
        if (row) {
            chart.push({
                date: item.date,
                amount: row.valueNis,
                price: row.price,
                quantity: row.nShares
            });
        }
    });
    // simgle table line (out of main table) of the asset at last day
    const lastDay = dataArray[0].data.find(r => r.assetId === assetId);
    if (lastDay) {
        let str = "<table>";
        str += "<tr>" + Object.entries(lastDay).map(e => `<th>${e[0]}</th>`).join("") + "</tr>";
        str += "<tr>" + Object.entries(lastDay).map(e => `<td>${e[1]}</td>`).join("") + "</tr>";
        document.getElementById("oneLine").innerHTML = str;
    }

    // table of day o day price tracking
    let str = "<table>";
    chart.forEach(item => {
        str += "<tr onclick=''>" + Object.entries(item).map(e => `<td>${e[1]}</td>`).join("") + "</tr>";
    });
    str += "</table>";
    document.getElementById("chart").innerHTML = str;

    // chart of day o day price tracking
    const canvas = document.getElementById("graphicChart");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath();
    const padding = 40;
    const maxAmount = Math.max(...chart.map(i => i.amount));
    const minAmount = Math.min(...chart.map(i => i.amount));
    const amountRange = maxAmount - minAmount;
    chart.toReversed().forEach((item, index) => {
        const x = index * (canvas.width - padding * 2) / (chart.length - 1) + padding;
        const y = canvas.height - ((item.amount - minAmount) / (amountRange || 1) * (canvas.height - padding * 2)) - padding;
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.strokeStyle = "blue";
    ctx.lineWidth = 2;
    ctx.stroke();
    //return chart;
}
document.getElementById("folderInput").addEventListener("change", async (event) => {

    const files = event.target.files;

    dataArray = [];

    for (const file of files) {

        if (!file.name.endsWith(".xlsx")) continue;

        const arrayBuffer = await file.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer);

        workbook.SheetNames.forEach(sheetName => {

            const sheet = workbook.Sheets[sheetName];
            const data = XLSX.utils.sheet_to_json(sheet);
            const processedData = data.slice(5).map((row) => {
                const processedRow = {};
                Object.entries(row).forEach(([key, value], index) => {
                    processedRow[fieldNames[index]] = convD(index, value);
                });
                return processedRow;
            });
            dataArray.push({ date: file.name.split(/[\_\.]/)[1], file: file.name, sheet: sheetName, data: processedData });

        });
    }
    dataArray.sort((a, b) => new Date(b.date) - new Date(a.date));
    let activeFilesStr = "";
    for (const item of dataArray) {
        console.log(`Date: ${item.date}, File: ${item.file}, Sheet: ${item.sheet}, Rows: ${item.data.length}`);
        activeFilesStr += `<b onclick="showData('${item.date}')">${item.date}</b> | ${item.data.length}<br>`;
    }

    const activeFilesDiv = document.getElementById("activeFiles");
    activeFilesDiv.innerHTML = activeFilesStr;
    assetFocus = null;

    window.buildData = function(data) {
        let str = "<table>";
        let row = data[0];
        str += "<tr>" + fieldDisplayNames.map(n => `<th>${n}</th>`).join("") + "</tr>";
        data.forEach(row => {
            const color = row.changePrecent > 0 ? "#d4edda" : row.changePrecent < 0 ? "#f8d7da" : "#fff";
            str += "<tr style='background-color: " + color + "; cursor:pointer;' onclick='trackStock(\"" + row.assetId + "\")'>" + fieldNames.map((n, i) => `<td>${convD(i, row[n])}</td>`).join("") + "</tr>";
        });
        return str + "</table>";
    }
    window.showData = function(date) {
        let dataDiv = document.getElementById("fileData");
        let dataDisplayStr = "";
        const item = dataArray.find(i => i.date === date);
        if (item) {
            const totalValue = item.data.reduce((sum, row) => sum + parseFloat(row.valueNis || 0), 0).toFixed(2);
            dataDisplayStr = `<h3>Data for ${item.date} value: ${totalValue}</h3><pre>${buildData(item.data.slice(0, -1))}</pre>`;
        }
        dataDiv.innerHTML = dataDisplayStr;
        
        const lastItem = dataArray[0];
        const lattItemDaysOfNoChangeInNumberOfStokes = lastItem.data.slice(0, -1).map(row => {
            const index = dataArray.slice(1).findIndex(prevItem => {
                const prevRow = prevItem.data.find(r => r.assetId === row.assetId);
                if (prevRow && prevRow.nShares === row.nShares) {
                    return false;
                }
                return true;
            });
            return { assetId: row.assetId, days: index === -1 ? dataArray.length - 1 : index };
        });

        let lastChangeStr = "<h3>Since</h3><pre><table><tr><th>ID</th><th>Days</th></tr>";
        lattItemDaysOfNoChangeInNumberOfStokes.forEach(item => {
            lastChangeStr += `<tr><td>${item.assetId}</td><td>${item.days}</td></tr>`;
        });
        lastChangeStr += "</table></pre>";
        document.getElementById("lastChange").innerHTML = lastChangeStr;

    }
    window.addEventListener("keydown", (event) => {
        switch (event.key) {
            case "ArrowUp":
                getNextStock(-1);
                break;
            case "ArrowDown":
                getNextStock(1);
                break;
            case "ArrowLeft":
            console.log("Moving left!");
            break;
            case "ArrowRight":
            console.log("Moving right!");
            break;
            default:
            return; // Quit when help items are not pressed
        }

        event.preventDefault();
        }, true);
});