function syncScroll(source) {
    const pdfViewer = document.getElementById('pdf-viewer');
    const textViewer = document.getElementById('text-viewer');
    
    if (source === 'pdf') {
        textViewer.scrollTop = (textViewer.scrollHeight * pdfViewer.scrollTop) / pdfViewer.scrollHeight;
    } else {
        pdfViewer.scrollTop = (pdfViewer.scrollHeight * textViewer.scrollTop) / textViewer.scrollHeight;
    }
} 