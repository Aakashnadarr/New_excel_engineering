
// Existing Clear button function
function clearAll() {
    document.querySelectorAll('input[type=text]').forEach(i => i.value = '');
    document.querySelectorAll('.ce-particulars').forEach(d => d.textContent = '');
}

// --- NEW: Auto-Calculate Invoice Math ---
document.addEventListener('DOMContentLoaded', () => {
    const itemRows = document.querySelectorAll('.tr-item');

    // Locate the exact rows for Totals and Taxes at the bottom
    const masterTable = document.querySelector('.master');
    const allRows = masterTable.querySelectorAll('tr');
    let totalRow, cgstRow, sgstRow, roundOffRow, grandTotalRow;

    allRows.forEach(row => {
        if (row.textContent.includes('TOTAL') && !row.textContent.includes('GRAND')) totalRow = row;
        if (row.textContent.includes('C.G.S.T')) cgstRow = row;
        if (row.textContent.includes('S.G.S.T')) sgstRow = row;
        if (row.textContent.includes('Round off')) roundOffRow = row;
        if (row.textContent.includes('GRAND TOTAL')) grandTotalRow = row;
    });

    // Percentage Inputs
    const cgstPercentInput = cgstRow.querySelector('.td-lbl input');
    const sgstPercentInput = sgstRow.querySelector('.td-lbl input');

    // Value Inputs (Rupees and Paise)
    const totalRsInput = totalRow.querySelector('.td-val input');
    const totalPInput = totalRow.querySelector('.td-p input');
    const cgstRsInput = cgstRow.querySelector('.td-val input');
    const cgstPInput = cgstRow.querySelector('.td-p input');
    const sgstRsInput = sgstRow.querySelector('.td-val input');
    const sgstPInput = sgstRow.querySelector('.td-p input');
    const roundOffRsInput = roundOffRow.querySelector('.td-val input');
    const roundOffPInput = roundOffRow.querySelector('.td-p input');
    const grandTotalRsInput = grandTotalRow.querySelector('.td-val input');
    const grandTotalPInput = grandTotalRow.querySelector('.td-p input');

    function calculate() {
        let subtotal = 0;

        // 1. Calculate each item row
        itemRows.forEach(row => {
            const inputs = row.querySelectorAll('.td-num input');
            const qty = parseFloat(inputs[0].value) || 0;
            const rate = parseFloat(inputs[1].value) || 0;

            if (qty > 0 && rate > 0) {
                const amount = qty * rate;
                subtotal += amount;

                const rs = Math.floor(amount);
                const p = Math.round((amount - rs) * 100);

                inputs[2].value = rs;
                inputs[3].value = p === 0 ? '00' : p.toString().padStart(2, '0');
            } else {
                inputs[2].value = '';
                inputs[3].value = '';
            }
        });

        // 2. Set Subtotal
        const subRs = Math.floor(subtotal);
        const subP = Math.round((subtotal - subRs) * 100);
        totalRsInput.value = subtotal > 0 ? subRs : '';
        totalPInput.value = subtotal > 0 ? (subP === 0 ? '00' : subP.toString().padStart(2, '0')) : '';

        // 3. Calculate Taxes
        const cgstPercent = parseFloat(cgstPercentInput.value) || 0;
        const sgstPercent = parseFloat(sgstPercentInput.value) || 0;

        const cgstAmount = subtotal * (cgstPercent / 100);
        const sgstAmount = subtotal * (sgstPercent / 100);

        if (cgstAmount > 0) {
            const crs = Math.floor(cgstAmount);
            const cp = Math.round((cgstAmount - crs) * 100);
            cgstRsInput.value = crs;
            cgstPInput.value = cp === 0 ? '00' : cp.toString().padStart(2, '0');
        } else {
            cgstRsInput.value = ''; cgstPInput.value = '';
        }

        if (sgstAmount > 0) {
            const srs = Math.floor(sgstAmount);
            const sp = Math.round((sgstAmount - srs) * 100);
            sgstRsInput.value = srs;
            sgstPInput.value = sp === 0 ? '00' : sp.toString().padStart(2, '0');
        } else {
            sgstRsInput.value = ''; sgstPInput.value = '';
        }

        // 4. Grand Total & Round Off
        if (subtotal > 0) {
            const totalWithTaxes = subtotal + cgstAmount + sgstAmount;
            const roundedGrandTotal = Math.round(totalWithTaxes);
            const roundOff = roundedGrandTotal - totalWithTaxes;

            if (roundOff !== 0) {
                const roSign = roundOff > 0 ? '+' : '';
                roundOffRsInput.value = roSign + roundOff.toFixed(2);
                roundOffPInput.value = '';
            } else {
                roundOffRsInput.value = '0.00';
                roundOffPInput.value = '';
            }

            grandTotalRsInput.value = roundedGrandTotal;
            grandTotalPInput.value = '00';
        } else {
            roundOffRsInput.value = ''; roundOffPInput.value = '';
            grandTotalRsInput.value = ''; grandTotalPInput.value = '';
        }
    }

    // Attach 'input' listeners to Qty, Rate, and Tax Percentages
    itemRows.forEach(row => {
        const inputs = row.querySelectorAll('.td-num input');
        inputs[0].addEventListener('input', calculate);
        inputs[1].addEventListener('input', calculate);
    });
    cgstPercentInput.addEventListener('input', calculate);
    sgstPercentInput.addEventListener('input', calculate);
});