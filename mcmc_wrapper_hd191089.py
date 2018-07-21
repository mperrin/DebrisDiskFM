import mcfostParameterTemplate
import copy
import subprocess

def mcmc_wrapper_hd191089(var_names = None, var_value = None, paraPath = None, calcSED = 'True', calcImage = 'True'):
    param_hd191089 = mcfostParameterTemplate.generateMcfostTemplate(1, [3], 1)

    resolution_stis = 0.05078
    resolution_gpi = 14.166e-3
    resolution_nicmos = 0.07565


    # # Fixed Parameters

    dist = 50.14
    param_hd191089['#Grid geometry and size']['row1']['n_rad'] = 35
    param_hd191089['#Maps']['row3']['distance'] = dist


    param_hd191089['#Density structure']['zone0']['row1']['gas-to-dust ratio'] = 0
    param_hd191089['#Density structure']['zone0']['row2']['reference radius'] = 45.3
    param_hd191089['#Density structure']['zone0']['row2']['scale height'] = 1.812
    param_hd191089['#Density structure']['zone0']['row2']['vertical profile exponent'] = 2

    param_hd191089['#Grain properties']['zone0']['species0']['row0']['Grain type'] = 'Mie'
    param_hd191089['#Grain properties']['zone0']['species1']['row0']['Grain type'] = 'Mie'
    param_hd191089['#Grain properties']['zone0']['species2']['row0']['Grain type'] = 'Mie'

    param_hd191089['#Grain properties']['zone0']['species0']['row3']['amax'] = 1e3
    param_hd191089['#Grain properties']['zone0']['species1']['row3']['amax'] = 1e3
    param_hd191089['#Grain properties']['zone0']['species2']['row3']['amax'] = 1e3

    param_hd191089['#Grain properties']['zone0']['species0']['row1']['Optical indices file'] = 'dlsi_opct.dat'
    param_hd191089['#Grain properties']['zone0']['species1']['row1']['Optical indices file'] = 'ac_opct.dat'
    param_hd191089['#Grain properties']['zone0']['species2']['row1']['Optical indices file'] = 'ice_opct.dat'

    param_hd191089['#Star properties']['star0']['row0']['Temp'] = 6440
    param_hd191089['#Star properties']['star0']['row0']['radius'] = 1.4
    param_hd191089['#Star properties']['star0']['row0']['M'] = 1.4
    param_hd191089['#Star properties']['star0']['row2']['fUV'] = 0.03


    # # Variables
    if var_names is None:
        var_names = ['inc', 'PA', 'm_disk', 
                     'Rc', 'R_in', 'alpha_in', 'alpha_out', 'porosity', 
                     'fmass_0', 'fmass_1', 
                     'a_min', 'Q_powerlaw']
    if var_value is None:    
        var_value = [59.7, 70, 1e-7, 
                         45.3, 20, 3.5,  3.5, 0.1,
                        0.05, 0.9,
                        1.0, 3.5]
                        
    # The MCFOST definition of inclination and position angle is not what we have been using.

    theta = dict(zip(var_names, var_value))

    for var_name in var_names:
        if var_name == 'inc':
            param_hd191089['#Maps']['row1']['imin'] = 180 - theta[var_name]
            param_hd191089['#Maps']['row1']['imax'] = 180 - theta[var_name]
            # Convert our definition to the MCFOST definition of inclination
        elif var_name == 'PA':
            param_hd191089['#Maps']['row4']['disk PA'] = 90 - theta[var_name]
            # Convert our definition to the MCFOST definition of position angle
        elif var_name == 'm_disk':
            param_hd191089['#Density structure']['zone0']['row1']['dust mass'] = theta[var_name]
        elif var_name == 'Rc':
            param_hd191089['#Density structure']['zone0']['row3']['Rc'] = theta[var_name]
            param_hd191089['#Density structure']['zone0']['row3']['Rout'] = 130*resolution_stis*dist # extent of the outer halo
        elif var_name == 'R_in':
            param_hd191089['#Density structure']['zone0']['row3']['Rin'] = theta[var_name]
        elif var_name == 'alpha_in':
            param_hd191089['#Density structure']['zone0']['row5']['surface density exponent/alpha_in'] = theta[var_name]
        elif var_name == 'alpha_out':
            param_hd191089['#Density structure']['zone0']['row5']['-gamma_exp/alpha_out'] = theta[var_name]
        elif var_name == 'porosity':
            param_hd191089['#Grain properties']['zone0']['species0']['row0']['porosity'] = theta[var_name]
            param_hd191089['#Grain properties']['zone0']['species1']['row0']['porosity'] = theta[var_name]
            param_hd191089['#Grain properties']['zone0']['species2']['row0']['porosity'] = theta[var_name]
        elif var_name == 'fmass_0':
            param_hd191089['#Grain properties']['zone0']['species0']['row0']['mass fraction'] = round(theta[var_name], 3)
            param_hd191089['#Grain properties']['zone0']['species1']['row0']['mass fraction'] = round(theta['fmass_1'], 3)
            param_hd191089['#Grain properties']['zone0']['species2']['row0']['mass fraction'] = round(1 - theta[var_name] - theta['fmass_1'], 3)
        elif var_name == 'a_min':
            param_hd191089['#Grain properties']['zone0']['species0']['row3']['amin'] = theta[var_name]
            param_hd191089['#Grain properties']['zone0']['species1']['row3']['amin'] = theta[var_name]
            param_hd191089['#Grain properties']['zone0']['species2']['row3']['amin'] = theta[var_name]
        elif var_name == 'Q_powerlaw':
            param_hd191089['#Grain properties']['zone0']['species0']['row3']['aexp'] = theta[var_name]
            param_hd191089['#Grain properties']['zone0']['species1']['row3']['aexp'] = theta[var_name]
            param_hd191089['#Grain properties']['zone0']['species2']['row3']['aexp'] = theta[var_name]


    # # Parameter File for HD191089

    param_hd191089_stis = copy.deepcopy(param_hd191089)
    stis_width = 316
    param_hd191089_stis['#Wavelength']['row3']['stokes parameters?'] = 'F'
    param_hd191089_stis['#Maps']['row0']['nx'] = stis_width
    param_hd191089_stis['#Maps']['row0']['ny'] = stis_width
    param_hd191089_stis['#Maps']['row0']['size'] = dist * stis_width * resolution_stis

    param_hd191089_nicmos = copy.deepcopy(param_hd191089)
    nicmos_width = 140
    param_hd191089_nicmos['#Wavelength']['row3']['stokes parameters?'] = 'F'
    param_hd191089_nicmos['#Maps']['row0']['nx'] = nicmos_width
    param_hd191089_nicmos['#Maps']['row0']['ny'] = nicmos_width
    param_hd191089_nicmos['#Maps']['row0']['size'] = dist * nicmos_width * resolution_nicmos


    param_hd191089_gpi = copy.deepcopy(param_hd191089)
    gpi_width = 218
    param_hd191089_gpi['#Wavelength']['row3']['stokes parameters?'] = 'T'
    param_hd191089_gpi['#Maps']['row0']['nx'] = gpi_width
    param_hd191089_gpi['#Maps']['row0']['ny'] = gpi_width
    param_hd191089_gpi['#Maps']['row0']['size'] = dist * gpi_width * resolution_gpi
    
    if paraPath is None:
        paraPath = './'
    mcfostParameterTemplate.display_file(param_hd191089_stis, paraPath + 'hd191089_stis.para')
    mcfostParameterTemplate.display_file(param_hd191089_nicmos, paraPath + 'hd191089_nicmos.para')
    mcfostParameterTemplate.display_file(param_hd191089_gpi, paraPath + 'hd191089_gpi.para')

    # # Run
    if calcSED:
        flag_run_mcfost_para_0 = subprocess.call('mcfost ' + paraPath + 'hd191089_stis.para', shell = True)

        if flag_run_mcfost_para_0 == 1:
            print('SED calculation is not performed, please check conflicting folder name.')

    if calcImage:
        flags_image = [1, 1, 1]
        flags_image[0] = subprocess.call('mcfost ' + paraPath + 'hd191089_stis.para -img 0.5852', shell = True)
        flags_image[1] = subprocess.call('mcfost ' + paraPath + 'hd191089_nicmos.para -img 1.12347', shell = True)
        flags_image[2] = subprocess.call('mcfost ' + paraPath + 'hd191089_nicmos.para -img 1.65', shell = True)

        if sum(flags_image) > 0:
            print('Image calculation is not performed for all the three wavelengths, please check conflicting folder name(s).')
    
mcmc_wrapper_hd191089()
