var filters = {
    pos_tag: "VB",
    region: "America",
    subset: "None",
    ngram: 1
}

const baseurl = document.querySelector('meta[name="baseurl"]').getAttribute('content');

var filename = `${baseurl}/assets/img/wordclouds/${filters.region}__${filters.subset}__${filters.pos_tag}__${filters.ngram}.jpg`

function update_ngram_value(new_value) {
    document.getElementById('ngram-value').textContent = new_value
}

function on_wordcloud_filter_change(new_filter) {
    filters[new_filter.key] = new_filter.value
    if (new_filter.key === "ngram") {
        update_ngram_value(new_filter.value)
    }
    filename = `${baseurl}/assets/img/wordclouds/${filters.region}__${filters.subset}__${filters.pos_tag}__${filters.ngram}.jpg`
    const wc_image = document.getElementById("wordcloud")
    wc_image.classList.add("wordcloud-image-hidden")
    // small transition
    setTimeout(() => {  
        // load the image after 500 ms
        wc_image.src = filename
    }, 300)
}
