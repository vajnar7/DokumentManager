$(document).ready(function() {
    // Load all documents on page load
    loadDocuments();

    // Search functionality
    $('#search-btn').click(function() {
        const query = $('#search-input').val().trim();
        if (query) {
            searchDocuments(query);
        } else {
            loadDocuments();
        }
    });

    $('#clear-search-btn').click(function() {
        $('#search-input').val('');
        loadDocuments();
    });

    // Enter key in search input
    $('#search-input').keypress(function(e) {
        if (e.which === 13) {
            $('#search-btn').click();
        }
    });

    // Add document form submission
    $('#add-document-form').submit(function(e) {
        e.preventDefault();
        addDocument();
    });

    // Edit document form submission
    $('#edit-document-form').submit(function(e) {
        e.preventDefault();
        updateDocument();
    });

    // Modal close
    $('.close').click(function() {
        $('#edit-modal').hide();
    });

    // Close modal when clicking outside
    $(window).click(function(e) {
        if (e.target.id === 'edit-modal') {
            $('#edit-modal').hide();
        }
    });

    function loadDocuments() {
        $.ajax({
            url: '/api/documents',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    displayDocuments(response.documents);
                } else {
                    showAlert('Error loading documents: ' + response.error, 'error');
                }
            },
            error: function(xhr) {
                showAlert('Error loading documents: ' + xhr.responseJSON?.error || 'Unknown error', 'error');
            }
        });
    }

    function searchDocuments(query) {
        $.ajax({
            url: '/api/documents/search',
            method: 'GET',
            data: { q: query },
            success: function(response) {
                if (response.success) {
                    displayDocuments(response.results);
                } else {
                    showAlert('Error searching documents: ' + response.error, 'error');
                }
            },
            error: function(xhr) {
                showAlert('Error searching documents: ' + xhr.responseJSON?.error || 'Unknown error', 'error');
            }
        });
    }

    function addDocument() {
        const formData = {
            title: $('#title').val(),
            sector: $('#sector').val(),
            author: $('#author').val(),
            content: $('#content').val()
        };

        $.ajax({
            url: '/api/documents',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    showAlert('Document added successfully!', 'success');
                    $('#add-document-form')[0].reset();
                    loadDocuments();
                } else {
                    showAlert('Error adding document: ' + response.error, 'error');
                }
            },
            error: function(xhr) {
                showAlert('Error adding document: ' + xhr.responseJSON?.error || 'Unknown error', 'error');
            }
        });
    }

    function editDocument(id) {
        $.ajax({
            url: `/api/documents/${id}`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    const doc = response.document;
                    $('#edit-id').val(doc.id);
                    $('#edit-title').val(doc.title);
                    $('#edit-sector').val(doc.sector);
                    $('#edit-author').val(doc.author);
                    $('#edit-content').val(doc.content);
                    $('#edit-modal').show();
                } else {
                    showAlert('Error loading document: ' + response.error, 'error');
                }
            },
            error: function(xhr) {
                showAlert('Error loading document: ' + xhr.responseJSON?.error || 'Unknown error', 'error');
            }
        });
    }

    function updateDocument() {
        const id = $('#edit-id').val();
        const formData = {
            title: $('#edit-title').val(),
            sector: $('#edit-sector').val(),
            author: $('#edit-author').val(),
            content: $('#edit-content').val()
        };

        $.ajax({
            url: `/api/documents/${id}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    showAlert('Document updated successfully!', 'success');
                    $('#edit-modal').hide();
                    loadDocuments();
                } else {
                    showAlert('Error updating document: ' + response.error, 'error');
                }
            },
            error: function(xhr) {
                showAlert('Error updating document: ' + xhr.responseJSON?.error || 'Unknown error', 'error');
            }
        });
    }

    function deleteDocument(id) {
        if (confirm('Are you sure you want to delete this document?')) {
            $.ajax({
                url: `/api/documents/${id}`,
                method: 'DELETE',
                success: function(response) {
                    if (response.success) {
                        showAlert('Document deleted successfully!', 'success');
                        loadDocuments();
                    } else {
                        showAlert('Error deleting document: ' + response.error, 'error');
                    }
                },
                error: function(xhr) {
                    showAlert('Error deleting document: ' + xhr.responseJSON?.error || 'Unknown error', 'error');
                }
            });
        }
    }

    function displayDocuments(documents) {
        const container = $('#documents-list');
        container.empty();

        if (documents.length === 0) {
            container.html('<p>No documents found.</p>');
            return;
        }

        documents.forEach(function(doc) {
            const docElement = $(`
                <div class="document-item">
                    <div class="document-header">
                        <h3 class="document-title">${escapeHtml(doc.title)}</h3>
                        <div class="document-actions">
                            <button class="edit-btn" data-id="${doc.id}">Edit</button>
                            <button class="delete-btn" data-id="${doc.id}">Delete</button>
                        </div>
                    </div>
                    <div class="document-meta">
                        ${doc.sector ? `<strong>Sector:</strong> ${escapeHtml(doc.sector)} | ` : ''}
                        ${doc.author ? `<strong>Author:</strong> ${escapeHtml(doc.author)} | ` : ''}
                        <strong>Created:</strong> ${doc.created_at ? new Date(doc.created_at).toLocaleString() : 'N/A'} |
                        <strong>Updated:</strong> ${doc.updated_at ? new Date(doc.updated_at).toLocaleString() : 'N/A'}
                    </div>
                    <div class="document-content">${escapeHtml(doc.content)}</div>
                </div>
            `);

            // Attach event handlers
            docElement.find('.edit-btn').click(function() {
                editDocument($(this).data('id'));
            });

            docElement.find('.delete-btn').click(function() {
                deleteDocument($(this).data('id'));
            });

            container.append(docElement);
        });
    }

    function showAlert(message, type) {
        // Remove existing alerts
        $('.alert').remove();

        const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
        const alert = $(`<div class="alert ${alertClass}">${message}</div>`);

        $('.container').prepend(alert);

        // Auto-hide after 5 seconds
        setTimeout(function() {
            alert.fadeOut();
        }, 5000);
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return (text || '').replace(/[&<>"']/g, function(m) { return map[m]; });
    }
});