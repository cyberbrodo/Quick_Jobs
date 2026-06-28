// ✅ GET USER FROM DJANGO SESSION (IMPORTANT 🔥)
let user = document.body.getAttribute("data-user");

// fallback (if needed)
if(!user){
    user = localStorage.getItem("username");
}

// ❌ if no login → redirect
if(!user){
    window.location.href="/login/";
}

// DOM
let searchInput = document.getElementById("searchInput");
let placeInput = document.getElementById("placeInput");
let categoryFilter = document.getElementById("categoryFilter");
let profileMenu = document.getElementById("profileMenu");
let profileName = document.getElementById("profileName");
let welcomeText = document.getElementById("welcomeText");
let jobList = document.getElementById("jobList");

// ✅ SHOW USER
profileName.innerText = user;
welcomeText.innerText = "Welcome, " + user;

let email = user;

// before @
let namePart = email.split("@")[0];

// short name (first 5 letters)
let shortName = namePart.substring(0,5);

profileName.innerText = shortName;
welcomeText.innerText = "Welcome, " + shortName;

// profile toggle
function toggleProfile(){
    profileMenu.classList.toggle("show");
}

// logout
function logout(){
    localStorage.removeItem("username");
    window.location.href="/login/";
}

// DATA
let jobs = JSON.parse(localStorage.getItem("jobs")) || [];
let savedKey = "savedJobs_"+user;
let savedJobs = JSON.parse(localStorage.getItem(savedKey)) || [];

// CATEGORY
function loadCategories(){
    let unique=[...new Set(jobs.map(j=>j.category))];
    unique.forEach(cat=>{
        if(!cat) return;
        let opt=document.createElement("option");
        opt.value=cat;
        opt.innerText=cat;
        categoryFilter.appendChild(opt);
    });
}

// FILTER
function applyFilter(){
    let text=searchInput.value.toLowerCase();
    let place=placeInput.value.toLowerCase();
    let cat=categoryFilter.value;

    let result=jobs.filter(j=>{
        return j.title.toLowerCase().includes(text) &&
               j.location.toLowerCase().includes(place) &&
               (cat==="" || j.category===cat);
    });

    showAllJobs(result);
}

// SHOW JOBS
function showAllJobs(list){
    jobList.innerHTML="";

    if(list.length===0){
        jobList.innerHTML="<p class='no-job'>No jobs available</p>";
        return;
    }

    list.forEach(job=>{

    let isSaved = savedJobs.find(j=>String(j.id)===String(job.id));

    let div=document.createElement("div");
    div.className="job-card";

    div.innerHTML=`
    <img src="${job.logo || 'logo.png'}"
         class="company-logo"
         onclick="filterCompany('${job.shop}')">

    <span class="save-icon"
          onclick="toggleSave('${job.id}')">
        ${isSaved ? "❤️":"🤍"}
    </span>

    <div class="job-main">
    <h3>${job.shop}</h3>
    <p><b>Job:</b> ${job.title}</p>
    <p class="exp">Experience: ${job.experience || 'Fresher'}</p>
    <p><b>Work Time:</b> ${job.workTime || 'Full Time'}</p>
    <p><b>Age:</b> ${job.age || 'NA'}</p>
    <p><b>Location:</b> ${job.location}</p>
    <p><b>Salary:</b> ${job.salary}</p>
    </div>

    <div class="contact-box">
    <button onclick="window.open('https://wa.me/91${job.phone}')">
    WhatsApp
    </button>
    </div>
    `;

    jobList.appendChild(div);
    });
}

// SAVE
function toggleSave(id){
    let job=jobs.find(j=>String(j.id)===String(id));
    if(!job) return;

    savedJobs.push(job);
    localStorage.setItem(savedKey,JSON.stringify(savedJobs));
    applyFilter();
}

// START
loadCategories();
showAllJobs(jobs);