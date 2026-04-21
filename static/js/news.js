
// Simple modal functions for news cards
function openModal(postId){
    var modal = new bootstrap.Modal(document.getElementById('modal' + postId));
    modal.show();
}