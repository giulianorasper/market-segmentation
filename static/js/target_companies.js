const targetCompaniesInput = document.getElementById('target_companies_input');
const targetCompaniesDropdown = document.getElementById('target_companies_dropdown');
const targetCompaniesSelectionsContainer = document.getElementById('target_companies_selections');
const targetCompaniesSelections = [];

targetCompaniesInput.addEventListener('input', function() {
  const searchText = targetCompaniesInput.value.toLowerCase();
  const matchedOptions = options.filter(option => option.toLowerCase().includes(searchText));
  showTargetCompaniesDropdown(matchedOptions);
});

targetCompaniesInput.addEventListener('keydown', function(event) {
  if (event.key === 'Tab' && targetCompaniesInput.value !== '') {
    event.preventDefault();
    const highlightedOption = targetCompaniesDropdown.querySelector('.highlighted');
    if (highlightedOption) {
      addTargetCompanySelection(highlightedOption.textContent);
      targetCompaniesInput.value = '';
      hideTargetCompaniesDropdown();
    } else if (targetCompaniesDropdown.children.length > 0) {
      const firstOption = targetCompaniesDropdown.children[0];
      firstOption.classList.add('highlighted');
      addTargetCompanySelection(firstOption.textContent);
      targetCompaniesInput.value = '';
      hideTargetCompaniesDropdown();
    }
  } else if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
    event.preventDefault();
    const highlightedOption = targetCompaniesDropdown.querySelector('.highlighted');
    if (highlightedOption) {
      const direction = event.key === 'ArrowUp' ? 'previous' : 'next';
      const newHighlightedOption = highlightedOption[direction + 'ElementSibling'];
      if (newHighlightedOption) {
        highlightedOption.classList.remove('highlighted');
        newHighlightedOption.classList.add('highlighted');
      }
    } else if (targetCompaniesDropdown.children.length > 0) {
      const firstOption = targetCompaniesDropdown.children[0];
      firstOption.classList.add('highlighted');
    }
  }
});

targetCompaniesInput.addEventListener('blur', function() {
  setTimeout(hideTargetCompaniesDropdown, 200);
});

targetCompaniesDropdown.addEventListener('click', function(event) {
  const selectedOption = event.target.closest('li');
  if (selectedOption) {
    addTargetCompanySelection(selectedOption.textContent);
    targetCompaniesInput.value = '';
    hideTargetCompaniesDropdown();
  }
});

function showTargetCompaniesDropdown(options) {
  targetCompaniesDropdown.innerHTML = '';
  options.forEach(option => {
    const li = document.createElement('li');
    li.textContent = option;
    li.addEventListener('click', function() {
      addTargetCompanySelection(option);
    });
    targetCompaniesDropdown.appendChild(li);
  });
  targetCompaniesDropdown.style.display = 'block';
}

function hideTargetCompaniesDropdown() {
  targetCompaniesDropdown.style.display = 'none';
}

function addTargetCompanySelection(companyName) {
  if (!targetCompaniesSelections.includes(companyName)) {
    const selectionElement = document.createElement('div');
    selectionElement.classList.add('selection');
    selectionElement.textContent = companyName;

    const removeButton = document.createElement('span');
    removeButton.classList.add('remove');
    removeButton.innerHTML = '&times;';

    removeButton.addEventListener('click', function() {
      removeTargetCompanySelection(selectionElement, companyName);
    });

    selectionElement.appendChild(removeButton);
    targetCompaniesSelectionsContainer.appendChild(selectionElement);

    targetCompaniesSelections.push(companyName);
  }
}

function removeTargetCompanySelection(selectionElement, companyName) {
  targetCompaniesSelectionsContainer.removeChild(selectionElement);

  const index = targetCompaniesSelections.indexOf(companyName);
  if (index > -1) {
    targetCompaniesSelections.splice(index, 1);
  }
}

// Function to retrieve the selected target companies
function getSelectedTargetCompanies() {
  return targetCompaniesSelections;
}



// Sample options (replace with your actual options)
const options = [
  'Service',
  'Versicherung',
  'Immobilien',
  'Marketing',
  'Kultur_Sozial',
  'Vereine',
  'Verwaltung_Beratung',
  'IT',
  'Logistik',
  'Einzelhandel',
  'Bau',
  'Großhandel',
  'Gesundheit_Fitness',
  'Finanzen',
  'Tourismus_Gastro',
  'Maschinen_Ingenieure',
  'Produzente_Hersteller_Industrie',
  'Handwerk',
  'Selbstständige',
  'Wissenschaft_Forschung'
];
