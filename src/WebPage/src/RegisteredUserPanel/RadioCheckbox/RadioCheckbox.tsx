import React, { JSX } from 'react';
import './RadioCheckbox.css';

export const RadioCheckbox = ({children}) : JSX.Element => {

    return (
        <>
            <input type="checkbox" id="checkboxInput">
                <label form="checkboxInput" className="toggleSwitch"> 
                    {children}
                </label>
            </input>
        </>
    )
}