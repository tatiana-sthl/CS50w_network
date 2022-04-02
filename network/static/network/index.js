function clearEditView(postId) {
    document.getElementById(`textarea_${postId}`).remove()
    document.getElementById(`save_${postId}`).remove()
    document.getElementById(`cancel_${postId}`).remove()

    document.getElementById(`post_content_${postId}`).style.display = 'block';
    document.getElementById(`edit_${postId}`).style.display = 'inline-block';
    document.getElementById(`post_likes_${postId}`).style.display = 'block';
}

function addValidationMessage(message, parentDiv) {
    const warningMessage = document.createElement('p');
    warningMessage.innerHTML = message;
    warningMessage.className = 'text-danger';

    document.getElementById(parentDiv).append(warningMessage);
}

function updateLikes(id, likes) {
    let likeCount = document.getElementById(`post_likecount_${id}`);

    likeCount.innerHTML = likes;
}

document.addEventListener('DOMContentLoaded', function() {

    document.addEventListener('click', event => {
        
        const element = event.target;

        // Like icon
        if (element.id.startsWith('post_likeicon_')) {
            let id = element.dataset.id;

            fetch(`/updatelike/${id}`, {
                method: "POST"
            })
            .then(function(response) {
                if (response.ok) {
                    return response.json()
                } else {
                    return Promise.reject('Error')
                }
            })
            .then(function(data) {
                const likes = data.likesCount;
                const likesPost = data.likesPost;

                let likeIcon = document.getElementById(`post_likeicon_${id}`);
                updateLikes(id, likes)

                if (likesPost) {
                    likeIcon.className = 'likeicon fa-solid fa-star';
                } else {
                    likeIcon.className = 'likeicon fa-regular fa-star';
                }
                
            })
            .catch(function(ex) {
                console.log("parsing failed", ex);
            });
        }

        // Edit button
        if (element.id.startsWith('edit_')) {
            const editButton = element;
            const postId = editButton.dataset.id;
            const postText = document.getElementById(`post_content_${postId}`);

            let textArea = document.createElement('textarea');
            textArea.innerHTML = postText.innerHTML;
            textArea.id = `textarea_${postId}`;
            textArea.className = 'form-control';
            document.getElementById(`post_contentgroup_${postId}`).append(textArea);

            // Hide and remove
            postText.style.display = 'none';
            document.getElementById(`post_likes_${postId}`).style.display = 'none';
            editButton.style.display = 'none';

            // Add cancel and save button
            const cancelButton = document.createElement('button');
            cancelButton.innerHTML = 'Cancel';
            cancelButton.className = 'badge rounded-pill bg-danger';
            cancelButton.id = `cancel_${postId}`

            const saveButton = document.createElement('button');
            saveButton.innerHTML = 'Save';
            saveButton.className = "badge rounded-pill bg-dark";
            saveButton.id = `save_${postId}`

            document.getElementById(`save_buttons_${postId}`).append(saveButton);

            // Event listener for cancel button
            cancelButton.addEventListener('click', function() {
                clearEditView(postId)
            })
            
            document.getElementById(`post_headline_${postId}`).append(cancelButton)
            
            saveButton.addEventListener('click', function() {
                
                textArea = document.getElementById(`textarea_${postId}`);

                fetch(`/editpost/${postId}`, {
                    method: 'POST',
                    body: JSON.stringify({
                        content: textArea.value,
                    })
                })
                
                .then(response => {
                    if (response.ok || response.status == 400) {
                        return response.json()
                    } else if(response.status === 404) {
                        clearEditView(postId)
                        editButton.style.display = 'none';
                        addValidationMessage("Not allowed", `post_contentgroup_${postId}`)
                        return Promise.reject('Error 404')
                    } else {
                        return Promise.reject('Error: ' + response.status)
                    } 
                })

                .then(result => {
                    if (!result.error) {
                        postText.innerHTML = result.content;
                        clearEditView(postId)
                    } else {
                        clearEditView(postId)
                        editButton.style.display = 'none';
                        addValidationMessage(result.error, `post_contentgroup_${postId}`)                      
                    }
                })
                .catch(error => {
                    console.error(error);
                })
            })
        }
    }) 
})

