import { Component, Prop, h } from '@stencil/core';

@Component({
  tag: 'electric-button',
  styleUrl: './styles.css',
  shadow: true
})

export class ElectricButton {

  // Indicate that name should be a public property on the component
  @Prop() link: string;
  @Prop() lightTheme: boolean = false;

  render() {
    return this.lightTheme == false ?
        <a href={this.link} class="electric-btn-dark">Install With Electric</a>
        :
        <a href={this.link} class='electric-btn-light'>Install With Electric</a>
  }
}