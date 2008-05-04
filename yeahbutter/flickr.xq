declare function local:flickr-query($method as xs:string, $params as xs:string*) {
  let $flickr-base := 'http://api.flickr.com/services/rest/?method=flickr.'
  return doc(string-join(
              (concat($flickr-base, $method),
               'api_key=7cb26a0fe491b6ac957a4a51872fb255',
               $params),
                  '&amp;'))
};


(: old base search :)
(: for $photo in local:flickr-query('photos.search', ('text=davis+square', 'per_page=10', 'sort=date-posted-asc'))/rsp/photos/photo :)

string-join(
  for $photo in local:flickr-query('groups.pools.getPhotos', ('group_id=88287362@N00', 'page=3', 'per_page=300'))/rsp/photos/photo
  let $id := data($photo/@id)
  let $secret := data($photo/@secret)
  let $url := concat('http://www.flickr.com/photos/',data($photo/@owner),'/', $id)
  return
    for $voter in data(local:flickr-query('photos.comments.getList', (concat('photo_id=', $id)))/rsp/comments/comment/@author)
      return string-join(($id, $voter, $url), '|')
  , '&#10;') 