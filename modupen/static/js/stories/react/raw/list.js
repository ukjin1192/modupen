var pagination = 1;

// Get stories with options
function getStories(num) {
	// Show loading icon
	$('#loading-icon').show();

	var data = {};

  data['filterOption'] = localStorage.getItem('filter_option') || 'processing';
  data['sortingOption'] = localStorage.getItem('sorting_option') || 'recent';
  data['pagination'] = num;

  if (num > 1) data['lastStoryID'] = $('.story').last().attr('data-story-id');

	$.ajax({
		url: '/stories/',
		type: 'GET',
		data: data
	}).done(function(data) {
		if (data.state == 'success') {
			switch (data.code) {
				case 1:
					$('#pagination').val(num);
					break;
				case 2:
					$('#pagination').val(num);
					$('#no-more-story').val('true');
					break;
				default:
					$('#pagination').val(num);
					break;
			}
		}
		// Failed to get more stories
		else {
			pagination = parseInt($('#pagination').val());
		}
	}).fail(function() {
		pagination = parseInt($('#pagination').val());
		alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
	}).always(function() {
		// Hide loading icon
		$('#loading-icon').hide();
		
		// Show no story message with icon if there is no story at all
		if ($('.story').length == 0) {
			$('#no-story-at-all').removeClass('hidden');
		}
	});
}
	
$(document).ready(function() {

	$(window).on('scroll', function() {
		
		// Show 'back to top' if scroll bar appears
		if ($(window).scrollTop() == 0) {
			$('#back-to-top').addClass('hidden');
		} else { 
			$('#back-to-top').removeClass('hidden');
		}
		
		// Get more stories
		if ($(window).scrollTop() > $(document).height() - $(window).height() - 100) {
			// Prevent from multiple request for same pagination
			if (parseInt($('#pagination').val()) == pagination && $('#no-more-story').val() == 'false') {
				pagination += 1;
				getStories(pagination);
			}
		}
	}); 

	$(document).on('click', '#update-story-list-option-btn', function() {
		// Show loading icon
		$('#loading-icon').show();
		
		// Prevent from double click
		$('#update-story-list-option-btn').button('loading');
		
		localStorage.setItem('filter_option', $('#filter-option').val());
		localStorage.setItem('sorting_option', $('#sorting-option').val());
		
		pagination = 1;
		$('#pagination').val('1');
		$('#no-more-story').val('false');
		
		getStories(pagination);
	});
});

// Remove fake block when image loaded
$('.story img').one('load', function() {
	var image = $(this);
	image.parent().removeClass('fake-block');
	image.removeClass('hidden');
}).each(function() {
	if (this.complete) $(this).load();
});

$(window).load(function() {
	// getStories(pagination);
});

var StoryList = React.createClass({
	getInitialState: function() {
    return {data: []};
  },
	componentDidMount: function() {
		var data = {};
		
		data['filterOption'] = localStorage.getItem('filter_option') || 'processing';
		data['sortingOption'] = localStorage.getItem('sorting_option') || 'recent';
		data['pagination'] = 1;
		
    $.ajax({
			url: '/stories/',
			type: 'GET',
			data: data,
      success: function(data) {
        this.setProps({data: data.stories});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
		var storyNodes = this.props.data.map(function (story) {
      return (
        <Story id={story.id} title={story.title} hasImage={story.has_image} imageURL={story.image_url} authorNickname={story.author_nickname} contributorsCount={story.contributors_count} hits={story.hits} commentsCount={story.comments_count} favoritesCount={story.favorites_count} state={story.state} closingDate={story.closing_date} />
      );
    });
    return (
      <div id='story-list'>
				{storyNodes}
      </div>
    );
  }
});

var Story = React.createClass({
	render: function() {
		return (
			<div className='story' data-story-id={this.props.id}>
				<a href={'/story/' + this.props.id + '/' }>
					<div className='position-relative fake-block'>
						<div className='alpha-blending'></div>
						{this.imageBlock()}
						<div className='caption-block-container'>
							<div className='caption-block'>
								<div className='caption-title'>
									{this.props.title}
								</div>
								<div className='space'></div>
								<div className='caption-contributors'>
									{this.contributorsBlock()}
								</div>
							</div>
						</div>
					</div>
					
					<div className='numeric-info-bar'>
						<span className='glyphicon glyphicon-eye-open' aria-hidden='true'></span> {this.props.hits}&emsp;
						<span className='glyphicon glyphicon-comment' aria-hidden='true'></span> {this.props.commentsCount}&emsp;
						<span className='glyphicon glyphicon-heart' aria-hidden='true'></span> {this.props.favoritesCount}&emsp;
						{/* TODO 완결 유무(state)에 따라 timeuntil, timesince filter 적용하기 */}
						<span className='glyphicon glyphicon-time' aria-hidden='true'></span> {this.props.closingDate}
					</div>
				</a>    
			</div>
		);
	},
	contributorsBlock: function() {
		if (this.props.contributorsCount > 1) {
			return (
				this.props.authorNickname + '님 외 ' + this.props.contributorsCount + '명이 함께 만듭니다'
			);
		} else {
			return (
				this.props.authorNickname + '님이 시작하셨습니다'
			);
		}
	},
	imageBlock: function() {
		if (this.props.hasImage) {
			return (
				<img src={this.convertToThumbnail(this.props.imageURL)} className='full-width hidden' onLoad={showImage(this.props.id)} />
			);
		} else {
			return ;
		}
	},
	convertToThumbnail: function(imageURL) {
		return imageURL.replace('/upload/', '/upload/w_360,h_120,c_thumb/');
	},
});

function showImage(storyID) {
	console.log(storyID);
	$('.story[data-story-id='+ storyID + ']').find('.fake-block').removeClass('fake-block');
	$('.story[data-story-id='+ storyID + ']').find('img').removeClass('hidden');
}

React.render(
	<StoryList data={[]} />,
	document.getElementById('content')
);
