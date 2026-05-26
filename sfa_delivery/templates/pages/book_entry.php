<?php
use SFA\Lib\Template;
$page_title = 'ספר גידולים';
ob_start();
?>
<section>
  <h1>ספר גידולים</h1>
  <div class="entry-cards">
    <a href="/crop-book/questions/">שאלות נפוצות</a>
    <a href="/crop-book/family/">משפחות</a>
    <a href="/crop-book/table/">טבלת גידולים</a>
    <a href="/crop-book/search/">חיפוש</a>
  </div>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
